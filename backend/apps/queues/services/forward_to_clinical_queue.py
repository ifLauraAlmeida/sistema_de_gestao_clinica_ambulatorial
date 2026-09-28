"""Encaminhamento da recepção para a fila do profissional."""

import uuid

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.encounters.models import EncounterStatus
from apps.encounters.services.status_transitions import change_encounter_status
from apps.queues.models import QueueEntry, QueueEntryStatus, QueueType
from apps.queues.services.enqueue import enqueue_in_clinical_queue
from apps.queues.services.queue_entry_lookup import ensure_entry_is_active, lock_queue_entry


def forward_to_clinical_queue(
    reception_entry_id: uuid.UUID, *, forwarded_by: User, ip_address: str | None = None
) -> QueueEntry:
    """
    Finaliza a etapa da recepção e insere o paciente na fila do profissional.

    Exemplo:
        clinical_entry = forward_to_clinical_queue(entrada_recepcao.id, forwarded_by=atendente)
    """
    with transaction.atomic():
        reception_entry = lock_queue_entry(reception_entry_id, QueueType.RECEPTION)
        ensure_entry_is_active(reception_entry)
        reception_entry.status = QueueEntryStatus.FINISHED
        reception_entry.finished_at = timezone.now()
        reception_entry.save(update_fields=["status", "finished_at"])

        encounter = change_encounter_status(
            reception_entry.encounter,
            EncounterStatus.AGUARDANDO_PROFISSIONAL,
            changed_by=forwarded_by,
            ip_address=ip_address,
        )
        clinical_entry = enqueue_in_clinical_queue(encounter)
        record_audit_event(
            action=AuditAction.QUEUE_ENTRY_FORWARDED,
            user=forwarded_by,
            entity_type="queue_entry",
            entity_id=str(clinical_entry.pk),
            ip_address=ip_address,
            metadata={"ticket_code": encounter.ticket_code, "from_queue": "RECEPTION"},
        )
    return clinical_entry
