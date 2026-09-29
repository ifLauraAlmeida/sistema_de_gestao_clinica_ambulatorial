"""
Autorização contextual de acesso ao prontuário.

Ter perfil Médico NÃO autoriza acesso a qualquer paciente. O acesso existe
apenas enquanto o atendimento do paciente está na fila ATIVA do próprio
médico, na especialidade permitida. Finalizar o atendimento (ATENDIDO) revoga
esse vínculo, sem alterar os registros clínicos existentes.
"""

from dataclasses import dataclass
from enum import StrEnum

from apps.accounts.access_permissions import AccessPermission, user_has_permission
from apps.accounts.models import User
from apps.encounters.active_link import find_active_link_denial
from apps.encounters.models import Encounter


class AccessReason(StrEnum):
    ADMINISTRATIVE_ACCESS = "administrative_access"
    ACTIVE_QUEUE_ENCOUNTER = "active_queue_encounter"
    ROLE_WITHOUT_CLINICAL_ACCESS = "role_without_clinical_access"
    NO_PROFESSIONAL_PROFILE = "no_professional_profile"
    ENCOUNTER_OF_ANOTHER_PROFESSIONAL = "encounter_of_another_professional"
    ENCOUNTER_NOT_ACTIVE = "encounter_not_active"
    NOT_IN_ACTIVE_QUEUE = "not_in_active_queue"
    SPECIALTY_NOT_ALLOWED = "specialty_not_allowed"


@dataclass(frozen=True)
class AccessDecision:
    """Resultado da avaliação, com o motivo registrado na auditoria."""

    granted: bool
    reason: AccessReason


def evaluate_medical_record_view(user: User, encounter: Encounter) -> AccessDecision:
    """
    Decide se o usuário pode consultar prontuário e histórico clínico via este atendimento.

    Exemplo:
        evaluate_medical_record_view(medico, atendimento_na_fila_ativa).granted  # True
    """
    if user_has_permission(user, AccessPermission.MEDICAL_RECORD_VIEW_ANY):
        return AccessDecision(True, AccessReason.ADMINISTRATIVE_ACCESS)
    return _evaluate_active_queue_link(
        user, encounter, AccessPermission.MEDICAL_RECORD_VIEW_ACTIVE_PATIENT
    )


def evaluate_medical_record_update(user: User, encounter: Encounter) -> AccessDecision:
    """
    Decide se o usuário pode registrar evolução neste atendimento.

    Não há exceção administrativa: somente o médico com o paciente na fila ativa.
    """
    return _evaluate_active_queue_link(
        user, encounter, AccessPermission.MEDICAL_RECORD_UPDATE_ACTIVE_PATIENT
    )


def _evaluate_active_queue_link(
    user: User, encounter: Encounter, permission: AccessPermission
) -> AccessDecision:
    if not user_has_permission(user, permission):
        return AccessDecision(False, AccessReason.ROLE_WITHOUT_CLINICAL_ACCESS)
    denial = find_active_link_denial(user, encounter)
    if denial is not None:
        return AccessDecision(False, AccessReason(denial.value))
    return AccessDecision(True, AccessReason.ACTIVE_QUEUE_ENCOUNTER)
