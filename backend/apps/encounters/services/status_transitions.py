"""Transições de status do atendimento com histórico e auditoria."""

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.core.exceptions import StateConflictError
from apps.encounters.models import Encounter, EncounterStatus, EncounterStatusChange

S = EncounterStatus

ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    S.CHECK_IN_REALIZADO: frozenset({S.AGUARDANDO_PROFISSIONAL, S.NAO_COMPARECEU, S.CANCELADO}),
    S.AGUARDANDO_PROFISSIONAL: frozenset({S.CHAMADO, S.NAO_COMPARECEU, S.CANCELADO}),
    S.CHAMADO: frozenset({S.EM_ATENDIMENTO, S.ATENDIDO, S.NAO_COMPARECEU}),
    S.EM_ATENDIMENTO: frozenset({S.ATENDIDO}),
    S.ATENDIDO: frozenset(),
    S.NAO_COMPARECEU: frozenset(),
    S.CANCELADO: frozenset(),
}


def change_encounter_status(
    encounter: Encounter,
    new_status: EncounterStatus,
    *,
    changed_by: User,
    ip_address: str | None = None,
) -> Encounter:
    """
    Aplica uma transição de status válida, registrando histórico e auditoria.

    Deve ser chamada dentro de uma transação junto das demais alterações da
    operação (chamada, finalização etc.).

    Exemplo:
        change_encounter_status(atendimento, EncounterStatus.CHAMADO, changed_by=medico)
    """
    previous_status = encounter.status
    if new_status not in ALLOWED_TRANSITIONS[previous_status]:
        raise StateConflictError(
            f"Transição de status inválida: recebido='{previous_status}' → '{new_status}', "
            f"esperado um dos destinos: {', '.join(sorted(ALLOWED_TRANSITIONS[previous_status]))}"
            " (nenhum, se o atendimento já foi encerrado).",
            code="invalid_encounter_transition",
        )

    encounter.status = new_status
    encounter.save(update_fields=["status"])
    EncounterStatusChange.objects.create(
        encounter=encounter,
        previous_status=previous_status,
        new_status=new_status,
        changed_by=changed_by,
    )
    record_audit_event(
        action=AuditAction.ENCOUNTER_STATUS_CHANGED,
        user=changed_by,
        entity_type="encounter",
        entity_id=str(encounter.pk),
        ip_address=ip_address,
        metadata={"previous_status": previous_status, "new_status": new_status},
    )
    return encounter
