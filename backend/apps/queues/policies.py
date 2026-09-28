"""
Autorização contextual de chamadas.

O perfil não basta: a chamada depende do tipo de fila, do dono da fila
clínica, da especialidade e de uma sessão de trabalho no posto adequado.
"""

from apps.accounts.access_permissions import AccessPermission, user_has_permission
from apps.accounts.models import User
from apps.professionals.selectors import professional_attends_specialty
from apps.queues.models import QueueEntry, QueueType
from apps.workstations.models import StationType

_CALL_STATION_TYPES = {
    QueueType.RECEPTION: StationType.RECEPTION_DESK,
    QueueType.CLINICAL: StationType.CONSULTATION_ROOM,
}


def get_call_station_type(queue_type: str) -> StationType:
    """Tipo de posto a partir do qual a fila é chamada (guichê ou consultório)."""
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
