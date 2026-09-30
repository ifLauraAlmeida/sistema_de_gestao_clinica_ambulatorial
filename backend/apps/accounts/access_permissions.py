"""
Matriz de permissões por perfil (RBAC).

O perfil define apenas o que o usuário PODE tentar fazer. Regras que dependem
de contexto (fila, atendimento, sessão de trabalho, sala, especialidade) ficam
nas políticas de cada domínio, por exemplo `apps.medical_records.policies`.
"""

from collections.abc import Mapping
from enum import StrEnum

from apps.accounts.models import User, UserRole


class AccessPermission(StrEnum):
    """Permissões granulares verificadas no backend."""

    PATIENT_CREATE = "patient.create"
    PATIENT_VIEW_DEMOGRAPHICS = "patient.view_demographics"
    PATIENT_UPDATE_DEMOGRAPHICS = "patient.update_demographics"

    APPOINTMENT_VIEW = "appointment.view"
    APPOINTMENT_CREATE = "appointment.create"
    APPOINTMENT_UPDATE = "appointment.update"

    CHECKIN_CREATE = "checkin.create"

    RECEPTION_QUEUE_VIEW = "reception_queue.view"
    RECEPTION_QUEUE_CALL = "reception_queue.call"
    RECEPTION_QUEUE_FORWARD = "reception_queue.forward"

    CLINICAL_QUEUE_VIEW_OWN = "clinical_queue.view_own"
    CLINICAL_QUEUE_VIEW_INACTIVE_OWN = "clinical_queue.view_inactive_own"
    CLINICAL_QUEUE_CALL_OWN = "clinical_queue.call_own"
    CLINICAL_QUEUE_VIEW_ALL = "clinical_queue.view_all"
    CLINICAL_QUEUE_CALL_ANY = "clinical_queue.call_any"

    ENCOUNTER_START_OWN = "encounter.start_own"
    ENCOUNTER_COMPLETE_OWN = "encounter.complete_own"

    MEDICAL_RECORD_VIEW_ACTIVE_PATIENT = "medical_record.view_active_patient"
    MEDICAL_RECORD_UPDATE_ACTIVE_PATIENT = "medical_record.update_active_patient"
    MEDICAL_RECORD_VIEW_ANY = "medical_record.view_any"

    PROCEDURE_RECORD_UPDATE_OWN = "procedure_record.update_own"
    PROCEDURE_RECORD_VIEW_ANY = "procedure_record.view_any"

    CATALOG_VIEW = "catalog.view"

    BILLING_VIEW_HISTORY = "billing.view_history"
    BILLING_MANAGE = "billing.manage"

    REPORTS_VIEW_OWN = "reports.view_own"
    REPORTS_VIEW_ALL = "reports.view_all"

    USERS_MANAGE = "users.manage"
    AUDIT_VIEW = "audit.view"

    WORK_SESSION_RECEPTION_DESK = "work_session.reception_desk"
    WORK_SESSION_CONSULTATION_ROOM = "work_session.consultation_room"
    WORK_SESSION_EXAM_ROOM = "work_session.exam_room"


_ATENDENTE_PERMISSIONS = frozenset(
    {
        AccessPermission.PATIENT_CREATE,
        AccessPermission.PATIENT_VIEW_DEMOGRAPHICS,
        AccessPermission.PATIENT_UPDATE_DEMOGRAPHICS,
        AccessPermission.APPOINTMENT_VIEW,
        AccessPermission.APPOINTMENT_CREATE,
        AccessPermission.APPOINTMENT_UPDATE,
        AccessPermission.CHECKIN_CREATE,
        AccessPermission.RECEPTION_QUEUE_VIEW,
        AccessPermission.RECEPTION_QUEUE_CALL,
        AccessPermission.RECEPTION_QUEUE_FORWARD,
        AccessPermission.REPORTS_VIEW_OWN,
        AccessPermission.CATALOG_VIEW,
        AccessPermission.WORK_SESSION_RECEPTION_DESK,
    }
)

_MEDICO_PERMISSIONS = frozenset(
    {
        AccessPermission.CLINICAL_QUEUE_VIEW_OWN,
        AccessPermission.CLINICAL_QUEUE_VIEW_INACTIVE_OWN,
        AccessPermission.CLINICAL_QUEUE_CALL_OWN,
        AccessPermission.ENCOUNTER_START_OWN,
        AccessPermission.ENCOUNTER_COMPLETE_OWN,
        AccessPermission.MEDICAL_RECORD_VIEW_ACTIVE_PATIENT,
        AccessPermission.MEDICAL_RECORD_UPDATE_ACTIVE_PATIENT,
        AccessPermission.PROCEDURE_RECORD_UPDATE_OWN,
        AccessPermission.REPORTS_VIEW_OWN,
        AccessPermission.WORK_SESSION_CONSULTATION_ROOM,
    }
)

# Mesmas regras do médico: o acesso clínico continua dependendo da fila ativa.
_PROFISSIONAL_SAUDE_PERMISSIONS = _MEDICO_PERMISSIONS

# O técnico executa o exame do paciente da própria fila, mas não consulta
# prontuário nem histórico clínico (acesso mínimo necessário).
_TECNICO_PERMISSIONS = frozenset(
    {
        AccessPermission.CLINICAL_QUEUE_VIEW_OWN,
        AccessPermission.CLINICAL_QUEUE_VIEW_INACTIVE_OWN,
        AccessPermission.CLINICAL_QUEUE_CALL_OWN,
        AccessPermission.ENCOUNTER_START_OWN,
        AccessPermission.ENCOUNTER_COMPLETE_OWN,
        AccessPermission.PROCEDURE_RECORD_UPDATE_OWN,
        AccessPermission.REPORTS_VIEW_OWN,
        AccessPermission.WORK_SESSION_EXAM_ROOM,
    }
)

# O Gestor tem acesso administrativo total. Atos clínicos (registrar evolução,
# preencher o procedimento e iniciar/finalizar atendimento) permanecem
# exclusivos do profissional responsável: são registros assistenciais.
_GESTOR_PERMISSIONS = frozenset(AccessPermission) - {
    AccessPermission.MEDICAL_RECORD_UPDATE_ACTIVE_PATIENT,
    AccessPermission.PROCEDURE_RECORD_UPDATE_OWN,
    AccessPermission.ENCOUNTER_START_OWN,
    AccessPermission.ENCOUNTER_COMPLETE_OWN,
}

ROLE_PERMISSIONS: Mapping[str, frozenset[AccessPermission]] = {
    UserRole.ATENDENTE: _ATENDENTE_PERMISSIONS,
    UserRole.MEDICO: _MEDICO_PERMISSIONS,
    UserRole.PROFISSIONAL_SAUDE: _PROFISSIONAL_SAUDE_PERMISSIONS,
    UserRole.TECNICO: _TECNICO_PERMISSIONS,
    UserRole.GESTOR: _GESTOR_PERMISSIONS,
}


def get_user_permissions(user: User) -> frozenset[AccessPermission]:
    """
    Retorna as permissões do perfil de um usuário ativo.

    Usuário inativo ou com perfil desconhecido não recebe permissão alguma.

    Exemplo:
        AccessPermission.PATIENT_CREATE in get_user_permissions(atendente)  # True
    """
    if not user.is_active:
        return frozenset()
    return ROLE_PERMISSIONS.get(user.role, frozenset())


def user_has_permission(user: User, permission: AccessPermission) -> bool:
    """
    Indica se o perfil do usuário concede a permissão.

    Exemplo:
        user_has_permission(medico, AccessPermission.CLINICAL_QUEUE_CALL_OWN)  # True
    """
    return permission in get_user_permissions(user)
