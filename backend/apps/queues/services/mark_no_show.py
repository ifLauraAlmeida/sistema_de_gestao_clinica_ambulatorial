"""Registro de não comparecimento do paciente chamado."""

import uuid

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.core.exceptions import StateConflictError
from apps.encounters.models import EncounterStatus
from apps.encounters.services.status_transitions import change_encounter_status
from apps.queues.models import QueueEntry, QueueEntryStatus, QueueType
from apps.queues.services.queue_entry_authorization import ensure_can_operate_queue_entry
from apps.queues.services.queue_entry_lookup import (
    ensure_entry_is_active,
    find_queue_entry,
    lock_queue_entry,
)


def mark_queue_entry_no_show(
    entry_id: uuid.UUID,
    queue_type: QueueType,
    *,
    marked_by: User,
    ip_address: str | None = None,
) -> QueueEntry:
    """
    Registra que o paciente não compareceu após ser chamado. Irreversível.

    Só é permitido para senhas já chamadas ao menos uma vez: o paciente pode
    não ter ouvido a primeira chamada e deve ser rechamado antes. O atendimento
    passa a NAO_COMPARECEU e deixa de autorizar acesso clínico; os registros
    permanecem armazenados.

    Exemplo:
        mark_queue_entry_no_show(entrada.id, QueueType.CLINICAL, marked_by=medico)
    """
    # Executado fora da transação: a auditoria da negação precisa persistir.
    ensure_can_operate_queue_entry(marked_by, find_queue_entry(entry_id, queue_type), ip_address)

    with transaction.atomic():
        entry = lock_queue_entry(entry_id, queue_type)
        ensure_entry_is_active(entry)
        _ensure_was_called(entry)
        previous_status = entry.encounter.status
        entry.status = QueueEntryStatus.NO_SHOW
        entry.finished_at = timezone.now()
        entry.save(update_fields=["status", "finished_at"])
        change_encounter_status(
            entry.encounter,
            EncounterStatus.NAO_COMPARECEU,
            changed_by=marked_by,
            ip_address=ip_address,
        )
        record_audit_event(
            action=AuditAction.QUEUE_ENTRY_NO_SHOW,
            user=marked_by,
            entity_type="queue_entry",
            entity_id=str(entry.pk),
            ip_address=ip_address,
            metadata={
                "ticket_code": entry.encounter.ticket_code,
                "queue_type": entry.queue_type,
                "call_attempts": entry.calls.count(),
                "previous_status": previous_status,
                "new_status": EncounterStatus.NAO_COMPARECEU,
            },
        )
    return entry


def _ensure_was_called(entry: QueueEntry) -> None:
    if entry.status == QueueEntryStatus.CALLED:
        return
    raise StateConflictError(
        f"Senha {entry.encounter.ticket_code} ainda não foi chamada: status='{entry.status}', "
        "esperado CALLED. Chame o paciente antes de registrar o não comparecimento.",
        code="queue_entry_not_called",
    )
