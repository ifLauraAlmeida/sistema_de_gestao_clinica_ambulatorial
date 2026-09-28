"""Início do atendimento pelo médico responsável (status EM_ATENDIMENTO)."""

import uuid

from django.db import transaction

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.encounters.models import Encounter, EncounterStatus
from apps.encounters.services.responsible_professional import (
    ensure_responsible_professional,
    get_encounter,
)
from apps.encounters.services.status_transitions import change_encounter_status


def start_encounter(
    encounter_id: uuid.UUID, *, started_by: User, ip_address: str | None = None
) -> Encounter:
    """
    Registra que o paciente chamado entrou no consultório.

    Só é possível a partir de CHAMADO; o paciente continua na fila ativa até a
    finalização.

    Exemplo:
        start_encounter(atendimento.id, started_by=medico)
    """
    # Verificado fora da transação: a auditoria da negação precisa persistir.
    ensure_responsible_professional(get_encounter(encounter_id), started_by, ip_address)

    with transaction.atomic():
        encounter = get_encounter(encounter_id, for_update=True)
        change_encounter_status(
            encounter, EncounterStatus.EM_ATENDIMENTO, changed_by=started_by, ip_address=ip_address
        )
        record_audit_event(
            action=AuditAction.ENCOUNTER_STARTED,
            user=started_by,
            entity_type="encounter",
            entity_id=str(encounter.pk),
            ip_address=ip_address,
        )
    return encounter
