"""Inclusão de atendimentos nas filas."""

from apps.encounters.models import Encounter
from apps.queues.models import QueueEntry, QueueType


def enqueue_in_reception(encounter: Encounter) -> QueueEntry:
    """
    Coloca o atendimento na fila compartilhada da recepção.

    Exemplo:
        enqueue_in_reception(atendimento_recem_criado)
    """
    return QueueEntry.objects.create(encounter=encounter, queue_type=QueueType.RECEPTION)


def enqueue_in_clinical_queue(encounter: Encounter) -> QueueEntry:
    """
    Coloca o atendimento na fila ativa do profissional responsável.

    Exemplo:
        enqueue_in_clinical_queue(atendimento_liberado)
    """
    return QueueEntry.objects.create(
        encounter=encounter,
        queue_type=QueueType.CLINICAL,
        professional=encounter.professional,
    )
