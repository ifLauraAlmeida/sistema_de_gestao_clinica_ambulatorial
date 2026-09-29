"""
Vínculo assistencial ativo entre um profissional e um atendimento.

Existe apenas enquanto o atendimento está na fila ativa do próprio profissional,
na especialidade em que ele atua. É a base das autorizações clínicas
(prontuário) e de execução de procedimentos.
"""

from enum import StrEnum

from apps.accounts.models import User
from apps.encounters.models import Encounter
from apps.professionals.selectors import (
    get_active_professional_for_user,
    professional_attends_specialty,
)
from apps.queues.models import ACTIVE_QUEUE_ENTRY_STATUSES, QueueType


class ActiveLinkDenial(StrEnum):
    """Motivo pelo qual não há vínculo ativo (registrado na auditoria)."""

    NO_PROFESSIONAL_PROFILE = "no_professional_profile"
    ENCOUNTER_OF_ANOTHER_PROFESSIONAL = "encounter_of_another_professional"
    ENCOUNTER_NOT_ACTIVE = "encounter_not_active"
    NOT_IN_ACTIVE_QUEUE = "not_in_active_queue"
    SPECIALTY_NOT_ALLOWED = "specialty_not_allowed"


def find_active_link_denial(user: User, encounter: Encounter) -> ActiveLinkDenial | None:
    """
    Retorna o motivo da ausência de vínculo ativo, ou `None` quando o vínculo existe.

    Não verifica permissões de perfil; cada política verifica a sua antes.

    Exemplo:
        find_active_link_denial(medico, atendimento_na_fila_ativa)  # None
    """
    professional = get_active_professional_for_user(user)
    if professional is None:
        return ActiveLinkDenial.NO_PROFESSIONAL_PROFILE
    if encounter.professional_id != professional.pk:
        return ActiveLinkDenial.ENCOUNTER_OF_ANOTHER_PROFESSIONAL
    if not encounter.is_clinically_active:
        return ActiveLinkDenial.ENCOUNTER_NOT_ACTIVE
    if not _is_in_active_clinical_queue(encounter):
        return ActiveLinkDenial.NOT_IN_ACTIVE_QUEUE
    if not professional_attends_specialty(professional, encounter.specialty_id):
        return ActiveLinkDenial.SPECIALTY_NOT_ALLOWED
    return None


def _is_in_active_clinical_queue(encounter: Encounter) -> bool:
    return encounter.queue_entries.filter(
        queue_type=QueueType.CLINICAL,
        professional_id=encounter.professional_id,
        status__in=ACTIVE_QUEUE_ENTRY_STATUSES,
    ).exists()
