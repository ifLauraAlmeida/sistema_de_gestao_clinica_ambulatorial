import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.catalog.models import Laterality, Service
from apps.patients.models import Patient
from apps.professionals.models import Professional, Specialty
from apps.scheduling.models import Appointment


class EncounterStatus(models.TextChoices):
    """Etapas do atendimento (subconjunto do escopo, seção 12)."""

    CHECK_IN_REALIZADO = "CHECK_IN_REALIZADO", "Check-in realizado"
    AGUARDANDO_PROFISSIONAL = "AGUARDANDO_PROFISSIONAL", "Aguardando profissional"
    CHAMADO = "CHAMADO", "Chamado"
    EM_ATENDIMENTO = "EM_ATENDIMENTO", "Em atendimento"
    ATENDIDO = "ATENDIDO", "Atendido"
    NAO_COMPARECEU = "NAO_COMPARECEU", "Não compareceu"
    CANCELADO = "CANCELADO", "Cancelado"


# Enquanto o atendimento está nestas etapas ele pertence à fila ATIVA do
# profissional, e somente nelas existe vínculo que autoriza acesso clínico.
CLINICALLY_ACTIVE_STATUSES = (
    EncounterStatus.AGUARDANDO_PROFISSIONAL,
    EncounterStatus.CHAMADO,
    EncounterStatus.EM_ATENDIMENTO,
)


class Encounter(models.Model):
    """
    Atendimento de um paciente em um dia, com profissional e especialidade.

    Atendimentos nunca são apagados: finalizar muda o status e preserva
    paciente, profissional, especialidade, horários e registros vinculados.
    A senha (`ticket_code`) acompanha o paciente por todas as etapas do dia.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="encounters")
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="encounter",
    )
    professional = models.ForeignKey(
        Professional, on_delete=models.PROTECT, related_name="encounters"
    )
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, related_name="+")
    # Copiados do agendamento no check-in: o que será realizado neste atendimento.
    service = models.ForeignKey(
        Service, on_delete=models.PROTECT, null=True, blank=True, related_name="encounters"
    )
    laterality = models.CharField(
        "lateralidade", max_length=16, choices=Laterality.choices, blank=True, default=""
    )
    with_sedation = models.BooleanField("com sedação", default=False)
    ticket_code = models.CharField("senha", max_length=12)
    service_date = models.DateField("data do atendimento", default=timezone.localdate)
    status = models.CharField(
        max_length=32, choices=EncounterStatus.choices, default=EncounterStatus.CHECK_IN_REALIZADO
    )
    checked_in_at = models.DateTimeField("chegada", default=timezone.now)
    completed_at = models.DateTimeField("finalização", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )

    class Meta:
        verbose_name = "atendimento"
        verbose_name_plural = "atendimentos"
        ordering = ("checked_in_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("service_date", "ticket_code"), name="encounter_unique_daily_ticket"
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=EncounterStatus.values),
                name="encounter_status_valid",
            ),
            models.CheckConstraint(
                condition=~models.Q(status=EncounterStatus.ATENDIDO)
                | models.Q(completed_at__isnull=False),
                name="encounter_completed_has_timestamp",
            ),
        ]
        indexes = [
            models.Index(fields=("professional", "status"), name="encounter_professional_idx"),
            models.Index(fields=("service_date", "status"), name="encounter_service_date_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.ticket_code} — {self.service_date:%d/%m/%Y}"

    @property
    def is_clinically_active(self) -> bool:
        return self.status in CLINICALLY_ACTIVE_STATUSES


class EncounterStatusChange(models.Model):
    """Histórico de mudanças de status: quem, quando, estado anterior e novo."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(
        Encounter, on_delete=models.PROTECT, related_name="status_changes"
    )
    previous_status = models.CharField(max_length=32, blank=True, default="")
    new_status = models.CharField(max_length=32, choices=EncounterStatus.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "mudança de status do atendimento"
        verbose_name_plural = "mudanças de status do atendimento"
        ordering = ("changed_at",)

    def __str__(self) -> str:
        return f"{self.previous_status or '—'} → {self.new_status}"
