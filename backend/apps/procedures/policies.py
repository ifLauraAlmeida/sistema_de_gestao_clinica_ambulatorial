"""
Autorização para consultar e preencher o procedimento de um atendimento.

Quem executa (técnico, médico ou profissional de saúde responsável) acessa
apenas enquanto o atendimento está na própria fila ativa. O gestor consulta
sem preencher. O acesso não inclui prontuário nem histórico clínico.
"""

from dataclasses import dataclass

from apps.accounts.access_permissions import AccessPermission, user_has_permission
from apps.accounts.models import User
from apps.encounters.active_link import find_active_link_denial
from apps.encounters.models import Encounter


@dataclass(frozen=True)
class ProcedureAccess:
    """Resultado da avaliação, com o motivo registrado na auditoria."""

    can_view: bool
    can_edit: bool
    reason: str


def evaluate_procedure_access(user: User, encounter: Encounter) -> ProcedureAccess:
    """
    Decide se o usuário pode ver e/ou preencher o procedimento do atendimento.

    Exemplo:
        evaluate_procedure_access(tecnico, atendimento_na_fila_ativa).can_edit  # True
    """
    if user_has_permission(user, AccessPermission.PROCEDURE_RECORD_UPDATE_OWN):
        denial = find_active_link_denial(user, encounter)
        if denial is None:
            return ProcedureAccess(True, True, "active_queue_encounter")
        if not user_has_permission(user, AccessPermission.PROCEDURE_RECORD_VIEW_ANY):
            return ProcedureAccess(False, False, str(denial))
    if user_has_permission(user, AccessPermission.PROCEDURE_RECORD_VIEW_ANY):
        return ProcedureAccess(True, False, "administrative_access")
    return ProcedureAccess(False, False, "role_without_procedure_access")
