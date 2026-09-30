"""
Descrição legível das ações e motivos gravados na auditoria.

Os códigos gravados nunca mudam; aqui ficam apenas nomes em português,
categorias usadas nos filtros e a indicação de acesso negado.
"""

from collections.abc import Mapping
from enum import StrEnum

from apps.audit.actions import AuditAction

A = AuditAction


class AuditCategory(StrEnum):
    ACCESS = "ACCESS"
    CLINICAL = "CLINICAL"
    QUEUE = "QUEUE"
    REGISTRY = "REGISTRY"
    WORKSTATION = "WORKSTATION"
    FINANCIAL = "FINANCIAL"
    AUDIT = "AUDIT"


CATEGORY_LABELS: Mapping[AuditCategory, str] = {
    AuditCategory.ACCESS: "Acesso ao sistema",
    AuditCategory.CLINICAL: "Prontuário e procedimentos",
    AuditCategory.QUEUE: "Filas e atendimento",
    AuditCategory.REGISTRY: "Cadastro e agenda",
    AuditCategory.WORKSTATION: "Postos de trabalho",
    AuditCategory.FINANCIAL: "Financeiro e autorizações",
    AuditCategory.AUDIT: "Consulta à auditoria",
}

# Ação → (nome exibido, categoria)
_ACTIONS: Mapping[str, tuple[str, AuditCategory]] = {
    A.LOGIN_SUCCESS: ("Login realizado", AuditCategory.ACCESS),
    A.LOGIN_FAILED: ("Login com falha", AuditCategory.ACCESS),
    A.LOGOUT: ("Logout", AuditCategory.ACCESS),
    A.ACCESS_DENIED: ("Acesso negado", AuditCategory.ACCESS),
    A.WORK_SESSION_STARTED: ("Sessão de trabalho iniciada", AuditCategory.WORKSTATION),
    A.WORK_SESSION_ENDED: ("Sessão de trabalho encerrada", AuditCategory.WORKSTATION),
    A.PATIENT_CREATED: ("Paciente cadastrado", AuditCategory.REGISTRY),
    A.PATIENT_UPDATED: ("Cadastro de paciente alterado", AuditCategory.REGISTRY),
    A.APPOINTMENT_CREATED: ("Agendamento criado", AuditCategory.REGISTRY),
    A.APPOINTMENT_UPDATED: ("Agendamento alterado", AuditCategory.REGISTRY),
    A.CHECK_IN_CREATED: ("Check-in realizado", AuditCategory.REGISTRY),
    A.ENCOUNTER_STATUS_CHANGED: ("Status do atendimento alterado", AuditCategory.QUEUE),
    A.ENCOUNTER_STARTED: ("Atendimento iniciado", AuditCategory.QUEUE),
    A.ENCOUNTER_COMPLETED: ("Atendimento finalizado", AuditCategory.QUEUE),
    A.QUEUE_TICKET_CALLED: ("Senha chamada", AuditCategory.QUEUE),
    A.QUEUE_ENTRY_FORWARDED: ("Encaminhado à fila do profissional", AuditCategory.QUEUE),
    A.QUEUE_ENTRY_NO_SHOW: ("Não comparecimento registrado", AuditCategory.QUEUE),
    A.MEDICAL_RECORD_VIEW_GRANTED: ("Prontuário aberto", AuditCategory.CLINICAL),
    A.MEDICAL_RECORD_VIEW_DENIED: ("Prontuário negado", AuditCategory.CLINICAL),
    A.CLINICAL_NOTE_CREATED: ("Evolução clínica registrada", AuditCategory.CLINICAL),
    A.PROCEDURE_RECORD_VIEW_GRANTED: ("Procedimento aberto", AuditCategory.CLINICAL),
    A.PROCEDURE_RECORD_VIEW_DENIED: ("Procedimento negado", AuditCategory.CLINICAL),
    A.PROCEDURE_RECORD_SAVED: ("Procedimento registrado", AuditCategory.CLINICAL),
    A.AUDIT_VIEWED: ("Auditoria consultada", AuditCategory.AUDIT),
    A.AUDIT_EXPORTED: ("Auditoria exportada", AuditCategory.AUDIT),
}

DENIAL_ACTIONS = frozenset(
    {
        A.ACCESS_DENIED,
        A.LOGIN_FAILED,
        A.MEDICAL_RECORD_VIEW_DENIED,
        A.PROCEDURE_RECORD_VIEW_DENIED,
    }
)

REASON_LABELS: Mapping[str, str] = {
    "active_queue_encounter": "paciente na fila ativa do profissional",
    "administrative_access": "acesso administrativo do gestor",
    "encounter_not_active": "atendimento não está ativo (ainda na recepção ou já finalizado)",
    "encounter_of_another_professional": "atendimento de outro profissional",
    "no_professional_profile": "usuário sem cadastro de profissional",
    "not_in_active_queue": "paciente fora da fila ativa",
    "specialty_not_allowed": "especialidade não atendida pelo profissional",
    "role_without_clinical_access": "perfil sem acesso clínico",
    "role_without_procedure_access": "perfil sem acesso a procedimentos",
    "not_responsible_professional": "não é o profissional responsável",
    "queue_call_not_allowed": "senha fora das filas do usuário",
    "station_type_not_allowed": "tipo de posto não permitido ao perfil",
    "clinical_queue_out_of_scope": "fila clínica de outro profissional",
}


def label_action(action: str) -> str:
    return _ACTIONS[action][0] if action in _ACTIONS else action


def category_of(action: str) -> AuditCategory | None:
    return _ACTIONS[action][1] if action in _ACTIONS else None


def actions_of_category(category: AuditCategory) -> list[str]:
    return [
        action for action, (_, action_category) in _ACTIONS.items() if action_category == category
    ]


def is_denial(action: str) -> bool:
    return action in DENIAL_ACTIONS


def label_reason(reason: object) -> str | None:
    if not isinstance(reason, str) or not reason:
        return None
    return REASON_LABELS.get(reason, reason)
