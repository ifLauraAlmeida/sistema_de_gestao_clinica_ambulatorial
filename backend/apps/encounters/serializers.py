from rest_framework import serializers

from apps.encounters.models import Encounter


class EncounterSummarySerializer(serializers.ModelSerializer[Encounter]):
    """Registro administrativo do atendimento, sem conteúdo clínico."""

    patient_name = serializers.CharField(source="patient.display_name", read_only=True)
    professional_name = serializers.CharField(
        source="professional.user.display_name", read_only=True
    )
    specialty_name = serializers.CharField(source="specialty.name", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Encounter
        fields = (
            "id",
            "ticket_code",
            "service_date",
            "patient",
            "patient_name",
            "professional",
            "professional_name",
            "specialty",
            "specialty_name",
            "status",
            "status_label",
            "checked_in_at",
            "completed_at",
        )
        read_only_fields = fields


class CheckInSerializer(serializers.Serializer[None]):
    """Entrada do check-in."""

    appointment_id = serializers.UUIDField()
