"""Consultas das filas e das chamadas."""

from datetime import date

from django.db.models import OuterRef, QuerySet, Subquery

from apps.professionals.models import Professional
from apps.queues.models import ACTIVE_QUEUE_ENTRY_STATUSES, QueueCall, QueueEntry, QueueType

RECENT_CALLS_LIMIT = 10


def _with_last_call(queryset: QuerySet[QueueEntry]) -> QuerySet[QueueEntry]:
    """Carrega relações exibidas e dados da última chamada sem consultas N+1."""
    last_call = QueueCall.objects.filter(queue_entry=OuterRef("pk")).order_by("-called_at")
    return queryset.select_related(
        "encounter__patient",
        "encounter__specialty",
        "encounter__service",
        "encounter__professional__user",
    ).annotate(
        last_call_destination=Subquery(last_call.values("destination_label")[:1]),
        last_called_at=Subquery(last_call.values("called_at")[:1]),
        last_call_attempt=Subquery(last_call.values("attempt_number")[:1]),
    )


def list_active_reception_queue(service_date: date) -> QuerySet[QueueEntry]:
    """
    Senhas aguardando ou chamadas na recepção, em ordem de chegada.

    Exemplo:
        list_active_reception_queue(timezone.localdate())
    """
    return _with_last_call(
        QueueEntry.objects.filter(
            queue_type=QueueType.RECEPTION,
            status__in=ACTIVE_QUEUE_ENTRY_STATUSES,
            encounter__service_date=service_date,
        )
    ).order_by("entered_at")


def list_clinical_queue(
    service_date: date, *, active: bool, professional: Professional | None = None
) -> QuerySet[QueueEntry]:
    """
    Fila clínica ativa (aguardando/chamado) ou inativa (finalizada) do dia.

    Sem `professional`, retorna as filas de todos os profissionais (uso do gestor).

    Exemplo:
        list_clinical_queue(hoje, active=True, professional=perfil_do_medico)
    """
    queryset = QueueEntry.objects.filter(
        queue_type=QueueType.CLINICAL, encounter__service_date=service_date
    )
    if active:
        queryset = queryset.filter(status__in=ACTIVE_QUEUE_ENTRY_STATUSES)
    else:
        queryset = queryset.exclude(status__in=ACTIVE_QUEUE_ENTRY_STATUSES)
    if professional is not None:
        queryset = queryset.filter(professional=professional)
    return _with_last_call(queryset).order_by("entered_at")


def list_recent_calls(queue_type: QueueType, service_date: date) -> QuerySet[QueueCall]:
    """Últimas chamadas do dia de um tipo de fila, da mais recente para a mais antiga."""
    return (
        QueueCall.objects.select_related("queue_entry__encounter__patient")
        .filter(queue_entry__queue_type=queue_type, called_at__date=service_date)
        .order_by("-called_at")[:RECENT_CALLS_LIMIT]
    )
