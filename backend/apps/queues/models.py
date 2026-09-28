import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.encounters.models import Encounter
from apps.professionals.models import Professional
from apps.workstations.models import StationType, WorkSession


class QueueType(models.TextChoices):
    RECEPTION = "RECEPTION", "Recepção"
    CLINICAL = "CLINICAL", "Clínica"


class QueueEntryStatus(models.TextChoices):
    WAITING = "WAITING", "Aguardando"
    CALLED = "CALLED", "Chamado"
    FINISHED = "FINISHED", "Finalizado"
    CANCELLED = "CANCELLED", "Cancelado"


ACTIVE_QUEUE_ENTRY_STATUSES = (QueueEntryStatus.WAITING, QueueEntryStatus.CALLED)


class QueueEntry(models.Model):
    """
    Posição de um atendimento em uma fila.

    A fila representa o estado (aguardando, chamado...), enquanto cada chamada
    é um evento separado em `QueueCall` (escopo, seção 15.7). Entradas
    finalizadas permanecem armazenadas: formam a fila inativa do profissional.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(Encounter, on_delete=models.PROTECT, related_name="queue_entries")
    queue_type = models.CharField(max_length=16, choices=QueueType.choices)
    # Dono da fila clínica. Nulo na fila da recepção, que é compartilhada.
    professional = models.ForeignKey(
        Professional,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="queue_entries",
    )
    status = models.CharField(
        max_length=16, choices=QueueEntryStatus.choices, default=QueueEntryStatus.WAITING
    )
    entered_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "entrada na fila"
        verbose_name_plural = "entradas na fila"
        ordering = ("entered_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("encounter", "queue_type"),
                condition=models.Q(status__in=ACTIVE_QUEUE_ENTRY_STATUSES),
                name="queue_entry_one_active_per_queue",
            ),
            models.CheckConstraint(
                condition=~models.Q(queue_type=QueueType.CLINICAL)
                | models.Q(professional__isnull=False),
                name="queue_entry_clinical_has_professional",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=QueueEntryStatus.values),
                name="queue_entry_status_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(queue_type__in=QueueType.values),
                name="queue_entry_type_valid",
            ),
        ]
        indexes = [
            models.Index(
                fields=("queue_type", "status", "entered_at"), name="queue_entry_list_idx"
            ),
            models.Index(fields=("professional", "status"), name="queue_entry_professional_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.encounter.ticket_code} ({self.get_queue_type_display()})"

    @property
    def is_active(self) -> bool:
        return self.status in ACTIVE_QUEUE_ENTRY_STATUSES


class QueueCall(models.Model):
    """
    Evento de chamada de uma senha para um destino.

    O destino é um snapshot: se o profissional trocar de consultório depois,
    esta chamada continua indicando o posto usado no momento.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    queue_entry = models.ForeignKey(QueueEntry, on_delete=models.PROTECT, related_name="calls")
    called_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    work_session = models.ForeignKey(
        WorkSession, on_delete=models.PROTECT, related_name="queue_calls"
    )
    destination_type = models.CharField(max_length=32, choices=StationType.choices)
    destination_id = models.UUIDField()
    destination_label = models.CharField(max_length=64)
    attempt_number = models.PositiveSmallIntegerField(default=1)
    called_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "chamada"
        verbose_name_plural = "chamadas"
        ordering = ("-called_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("queue_entry", "attempt_number"), name="queue_call_unique_attempt"
            ),
        ]
        indexes = [models.Index(fields=("-called_at",), name="queue_call_recent_idx")]

    def __str__(self) -> str:
        return f"{self.queue_entry.encounter.ticket_code} → {self.destination_label}"
