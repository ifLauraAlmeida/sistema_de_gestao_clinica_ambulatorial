from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.patients.models import Patient
from apps.professionals.models import Professional, Specialty
from apps.scheduling.models import MANUALLY_SETTABLE_APPOINTMENT_STATUSES, Appointment


class AppointmentSerializer(serializers.ModelSerializer[Appointment]):
    """Agendamento exibido na agenda (somente dados administrativos)."""

    patient_name = serializers.CharField(source="patient.display_name", read_only=True)
    # Contato para a recepção confirmar a consulta ou avisar o paciente.
    patient_phone = serializers.CharField(source="patient.phone", read_only=True)
    professional_name = serializers.CharField(
        source="professional.user.display_name", read_only=True
    )
    specialty_name = serializers.CharField(source="specialty.name", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    ticket_code = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient",
            "patient_name",
            "patient_phone",
            "professional",
            "professional_name",
            "specialty",
            "specialty_name",
            "scheduled_for",
            "status",
            "status_label",
            "notes",
            "ticket_code",
        )
        read_only_fields = fields

    def get_ticket_code(self, appointment: Appointment) -> str | None:
        """Senha gerada no check-in; nula enquanto o paciente não chegou."""
        try:
            return str(appointment.encounter.ticket_code)
        except ObjectDoesNotExist:
            return None


class CreateAppointmentSerializer(serializers.Serializer[None]):
    """Entrada para criar agendamento."""

    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.filter(is_active=True))
    professional = serializers.PrimaryKeyRelatedField(
        queryset=Professional.objects.filter(is_active=True)
    )
    specialty = serializers.PrimaryKeyRelatedField(
        queryset=Specialty.objects.filter(is_active=True)
    )
    scheduled_for = serializers.DateTimeField()
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class UpdateAppointmentSerializer(serializers.Serializer[None]):
    """Alterações permitidas à recepção."""

    scheduled_for = serializers.DateTimeField(required=False)
    status = serializers.ChoiceField(choices=MANUALLY_SETTABLE_APPOINTMENT_STATUSES, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
