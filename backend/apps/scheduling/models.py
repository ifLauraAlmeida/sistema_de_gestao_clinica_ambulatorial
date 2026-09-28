import uuid

from django.conf import settings
from django.db import models

from apps.patients.models import Patient
from apps.professionals.models import Professional, Specialty


class AppointmentStatus(models.TextChoices):
    """Situação administrativa do agendamento."""

    AGENDADO = "AGENDADO", "Agendado"
    CONFIRMADO = "CONFIRMADO", "Confirmado"
    CHECK_IN_REALIZADO = "CHECK_IN_REALIZADO", "Check-in realizado"
    CANCELADO = "CANCELADO", "Cancelado"
    NAO_COMPARECEU = "NAO_COMPARECEU", "Não compareceu"


# Status que a recepção pode definir manualmente. CHECK_IN_REALIZADO só é
# definido pelo fluxo de check-in, que também cria o atendimento.
MANUALLY_SETTABLE_APPOINTMENT_STATUSES = (
    AppointmentStatus.AGENDADO,
    AppointmentStatus.CONFIRMADO,
    AppointmentStatus.CANCELADO,
    AppointmentStatus.NAO_COMPARECEU,
)

CHECK_IN_ELIGIBLE_APPOINTMENT_STATUSES = (
    AppointmentStatus.AGENDADO,
    AppointmentStatus.CONFIRMADO,
)


class Appointment(models.Model):
    """Consulta marcada para um paciente com um profissional e especialidade."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="appointments")
    professional = models.ForeignKey(
        Professional, on_delete=models.PROTECT, related_name="appointments"
    )
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, related_name="+")
    scheduled_for = models.DateTimeField("data e horário")
    status = models.CharField(
        max_length=32, choices=AppointmentStatus.choices, default=AppointmentStatus.AGENDADO
    )
    notes = models.TextField("observações", blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "agendamento"
        verbose_name_plural = "agendamentos"
        ordering = ("scheduled_for",)
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=AppointmentStatus.values),
                name="appointment_status_valid",
            ),
        ]
        indexes = [
            models.Index(fields=("scheduled_for",), name="appointment_scheduled_idx"),
            models.Index(
                fields=("professional", "scheduled_for"), name="appointment_professional_idx"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.patient} — {self.scheduled_for:%d/%m/%Y %H:%M}"
