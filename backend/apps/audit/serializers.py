from rest_framework import serializers

from apps.audit.models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer[AuditEvent]):
    username = serializers.CharField(source="user.username", read_only=True, default=None)

    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "timestamp",
            "action",
            "username",
            "entity_type",
            "entity_id",
            "ip_address",
            "metadata",
        )
        read_only_fields = fields


class AuditEventQuerySerializer(serializers.Serializer[None]):
    action = serializers.CharField(required=False, max_length=64)
    entity_type = serializers.CharField(required=False, max_length=64)
    entity_id = serializers.CharField(required=False, max_length=64)
