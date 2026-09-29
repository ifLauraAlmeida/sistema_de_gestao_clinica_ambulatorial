from rest_framework import serializers

from apps.queues.models import QueueCall, QueueEntry


class QueueEntrySerializer(serializers.ModelSerializer[QueueEntry]):
    """
    Senha na fila com dados administrativos (sem conteúdo clínico).

    Espera um queryset anotado por `apps.queues.selectors`.
    """

    encounter_id = serializers.UUIDField(source="encounter.id", read_only=True)
    ticket_code = serializers.CharField(source="encounter.ticket_code", read_only=True)
    patient_name = serializers.CharField(source="encounter.patient.display_name", read_only=True)
    specialty_name = serializers.CharField(source="encounter.specialty.name", read_only=True)
    service_name = serializers.CharField(
        source="encounter.service.name", read_only=True, default=None
    )
    laterality_label = serializers.CharField(
        source="encounter.get_laterality_display", read_only=True
    )
    professional_name = serializers.CharField(
        source="encounter.professional.user.display_name", read_only=True
    )
    encounter_status = serializers.CharField(source="encounter.status", read_only=True)
    encounter_status_label = serializers.CharField(
        source="encounter.get_status_display", read_only=True
    )
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    last_call_destination = serializers.CharField(read_only=True, allow_null=True, default=None)
    last_called_at = serializers.DateTimeField(read_only=True, allow_null=True, default=None)
    last_call_attempt = serializers.IntegerField(read_only=True, allow_null=True, default=None)

    class Meta:
        model = QueueEntry
        fields = (
            "id",
            "encounter_id",
            "queue_type",
            "ticket_code",
            "patient_name",
            "specialty_name",
            "service_name",
            "laterality_label",
            "professional_name",
            "status",
            "status_label",
            "encounter_status",
            "encounter_status_label",
            "entered_at",
            "finished_at",
            "last_call_destination",
            "last_called_at",
            "last_call_attempt",
        )
        read_only_fields = fields


class QueueCallSerializer(serializers.ModelSerializer[QueueCall]):
    """Chamada registrada, com destino histórico."""

    queue_entry_id = serializers.UUIDField(source="queue_entry.id", read_only=True)
    ticket_code = serializers.CharField(source="queue_entry.encounter.ticket_code", read_only=True)
    patient_name = serializers.CharField(
        source="queue_entry.encounter.patient.display_name", read_only=True
    )

    class Meta:
        model = QueueCall
        fields = (
            "id",
            "queue_entry_id",
            "ticket_code",
            "patient_name",
            "destination_type",
            "destination_label",
            "attempt_number",
            "called_at",
        )
        read_only_fields = fields
