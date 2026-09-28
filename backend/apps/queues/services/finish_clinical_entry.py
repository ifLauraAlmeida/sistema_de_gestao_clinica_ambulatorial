"""Encerramento da senha na fila clínica."""

from django.utils import timezone

from apps.encounters.models import Encounter
from apps.queues.models import ACTIVE_QUEUE_ENTRY_STATUSES, QueueEntryStatus, QueueType


def finish_clinical_queue_entry(encounter: Encounter) -> None:
    """
    Move a senha ativa do atendimento para a fila inativa do profissional.

    A entrada não é apagada: permanece como registro administrativo. Deve ser
    chamada dentro da transação que finaliza o atendimento.
    """
    encounter.queue_entries.filter(
        queue_type=QueueType.CLINICAL, status__in=ACTIVE_QUEUE_ENTRY_STATUSES
    ).update(status=QueueEntryStatus.FINISHED, finished_at=timezone.now())
