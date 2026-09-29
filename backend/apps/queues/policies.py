"""
Autorização contextual de chamadas.

O perfil não basta: a chamada depende do tipo de fila, do dono da fila
clínica, da especialidade e de uma sessão de trabalho no posto adequado.
"""

import uuid

from apps.accounts.access_permissions import AccessPermission, user_has_permission
from apps.accounts.models import User
from apps.core.exceptions import AccessDeniedError, ResourceNotFoundError
from apps.professionals.models import Professional
from apps.professionals.selectors import (
    get_active_professional_for_user,
    professional_attends_specialty,
)
from apps.queues.models import QueueEntry, QueueType
from apps.workstations.models import StationType

# A fila clínica é chamada do consultório (consultas, sessões) ou da sala de
# exames (raio-X, coleta, ultrassom...), conforme o posto de quem atende.
_CALL_STATION_TYPES: dict[QueueType, tuple[StationType, ...]] = {
    QueueType.RECEPTION: (StationType.RECEPTION_DESK,),
    QueueType.CLINICAL: (StationType.CONSULTATION_ROOM, StationType.EXAM_ROOM),
}


def get_call_station_types(queue_type: str) -> tuple[StationType, ...]:
    """Tipos de posto a partir dos quais a fila pode ser chamada."""
    return _CALL_STATION_TYPES[QueueType(queue_type)]


def can_call_queue_entry(user: User, entry: QueueEntry) -> bool:
    """
    Indica se o usuário pode chamar a senha desta entrada de fila.

    Exemplo:
        can_call_queue_entry(medico, entrada_da_propria_fila)  # True
        can_call_queue_entry(medico, entrada_de_outro_medico)  # False
    """
    if entry.queue_type == QueueType.RECEPTION:
        return user_has_permission(user, AccessPermission.RECEPTION_QUEUE_CALL)
    if user_has_permission(user, AccessPermission.CLINICAL_QUEUE_CALL_ANY):
        return True
    return user_has_permission(
        user, AccessPermission.CLINICAL_QUEUE_CALL_OWN
    ) and _is_own_clinical_entry(user, entry)


def _is_own_clinical_entry(user: User, entry: QueueEntry) -> bool:
    professional = entry.professional
    if professional is None or not professional.is_active or professional.user_id != user.pk:
        return False
    return professional_attends_specialty(professional, entry.encounter.specialty_id)


def resolve_clinical_queue_owner(
    user: User, *, active: bool, requested_professional_id: uuid.UUID | None
) -> Professional | None:
    """
    Define de qual profissional é a fila clínica que o usuário pode consultar.

    Retorna `None` quando o usuário pode ver as filas de todos (gestor sem
    filtro). Médicos só consultam a própria fila; pedir a de outro é negado.

    Exemplo:
        resolve_clinical_queue_owner(medico, active=True, requested_professional_id=None)
    """
    if user_has_permission(user, AccessPermission.CLINICAL_QUEUE_VIEW_ALL):
        return _find_professional(requested_professional_id)

    own_permission = (
        AccessPermission.CLINICAL_QUEUE_VIEW_OWN
        if active
        else AccessPermission.CLINICAL_QUEUE_VIEW_INACTIVE_OWN
    )
    own_professional = get_active_professional_for_user(user)
    if not user_has_permission(user, own_permission) or own_professional is None:
        raise ClinicalQueueAccessDeniedError("Você não possui fila clínica própria.")
    if requested_professional_id not in (None, own_professional.pk):
        raise ClinicalQueueAccessDeniedError("Você só pode consultar a sua própria fila clínica.")
    return own_professional


class ClinicalQueueAccessDeniedError(AccessDeniedError):
    """Tentativa de consultar fila clínica fora do escopo do usuário."""

    default_code = "clinical_queue_access_denied"


def _find_professional(professional_id: uuid.UUID | None) -> Professional | None:
    if professional_id is None:
        return None
    professional = Professional.objects.filter(pk=professional_id).first()
    if professional is None:
        raise ResourceNotFoundError(
            f"Profissional não encontrado: recebido={professional_id}.",
            code="professional_not_found",
        )
    return professional
