"""Localização e bloqueio de entradas de fila para operações de escrita."""

import uuid

from django.db.models import QuerySet

from apps.core.exceptions import ResourceNotFoundError, StateConflictError
from apps.queues.models import QueueEntry, QueueType


def find_queue_entry(entry_id: uuid.UUID, queue_type: QueueType) -> QueueEntry:
    """
    Busca a entrada garantindo que pertence à fila esperada, sem bloqueio.

    Usada para verificar autorização antes de abrir a transação, de modo que a
    auditoria de uma negação não seja desfeita pelo rollback.
    """
    return _get_entry_or_404(
        QueueEntry.objects.select_related("encounter", "professional"), entry_id, queue_type
    )


def lock_queue_entry(entry_id: uuid.UUID, queue_type: QueueType) -> QueueEntry:
    """
    Bloqueia a entrada (SELECT FOR UPDATE) garantindo que pertence à fila esperada.

    Deve ser usada dentro de `transaction.atomic()`.
    """
    return _get_entry_or_404(
        QueueEntry.objects.select_for_update(of=("self",)).select_related(
            "encounter", "professional"
        ),
        entry_id,
        queue_type,
    )


def _get_entry_or_404(
    queryset: QuerySet[QueueEntry], entry_id: uuid.UUID, queue_type: QueueType
) -> QueueEntry:
    entry = queryset.filter(pk=entry_id, queue_type=queue_type).first()
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
