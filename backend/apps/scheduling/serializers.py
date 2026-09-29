from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.catalog.models import LaboratoryExam, Laterality, Service
from apps.patients.models import Patient
from apps.professionals.models import Professional
from apps.scheduling.models import MANUALLY_SETTABLE_APPOINTMENT_STATUSES, Appointment
from apps.scheduling.service_options import build_preparation_summary


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
    service_name = serializers.CharField(source="service.name", read_only=True, default=None)
    service_type_label = serializers.CharField(
        source="service.get_service_type_display", read_only=True, default=None
    )
    duration_minutes = serializers.IntegerField(
        source="service.duration_minutes", read_only=True, default=None
    )
    laterality_label = serializers.CharField(source="get_laterality_display", read_only=True)
    laboratory_exam_names = serializers.SerializerMethodField()
    preparation = serializers.SerializerMethodField()

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
            "service",
            "service_name",
            "service_type_label",
            "duration_minutes",
            "laterality",
            "laterality_label",
            "with_sedation",
            "laboratory_exam_names",
            "preparation",
        )
        read_only_fields = fields

    def get_laboratory_exam_names(self, appointment: Appointment) -> list[str]:
        return [exam.name for exam in appointment.laboratory_exams.all()]

    def get_preparation(self, appointment: Appointment) -> str:
        return build_preparation_summary(
            appointment.service, list(appointment.laboratory_exams.all())
        )

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
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.filter(is_active=True))
    laterality = serializers.ChoiceField(
        choices=Laterality.choices, required=False, allow_blank=True, default=""
    )
    with_sedation = serializers.BooleanField(required=False, default=False)
    laboratory_exams = serializers.PrimaryKeyRelatedField(
        queryset=LaboratoryExam.objects.filter(is_active=True),
        many=True,
        required=False,
        default=list,
    )
    scheduled_for = serializers.DateTimeField()
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class UpdateAppointmentSerializer(serializers.Serializer[None]):
    """Alterações permitidas à recepção."""

    scheduled_for = serializers.DateTimeField(required=False)
    status = serializers.ChoiceField(choices=MANUALLY_SETTABLE_APPOINTMENT_STATUSES, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
