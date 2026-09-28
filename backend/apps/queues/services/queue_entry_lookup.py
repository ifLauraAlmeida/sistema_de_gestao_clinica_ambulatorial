"""Localização e bloqueio de entradas de fila para operações de escrita."""

import uuid

from apps.core.exceptions import ResourceNotFoundError, StateConflictError
from apps.queues.models import QueueEntry, QueueType


def lock_queue_entry(entry_id: uuid.UUID, queue_type: QueueType) -> QueueEntry:
    """
    Bloqueia a entrada (SELECT FOR UPDATE) garantindo que pertence à fila esperada.

    Deve ser usada dentro de `transaction.atomic()`.
    """
    entry = (
        QueueEntry.objects.select_for_update(of=("self",))
        .select_related("encounter", "professional")
        .filter(pk=entry_id, queue_type=queue_type)
        .first()
    )
    if entry is None:
        raise ResourceNotFoundError(
            f"Senha não encontrada na fila {queue_type.label}: recebido={entry_id}.",
            code="queue_entry_not_found",
        )
    return entry


def ensure_entry_is_active(entry: QueueEntry) -> None:
    """Rejeita operações sobre senhas já finalizadas ou canceladas."""
    if not entry.is_active:
        raise StateConflictError(
            f"Senha {entry.encounter.ticket_code} não está ativa: status='{entry.status}', "
            "esperado WAITING ou CALLED.",
            code="queue_entry_not_active",
        )
