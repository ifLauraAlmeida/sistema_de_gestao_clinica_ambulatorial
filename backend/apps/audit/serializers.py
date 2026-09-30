from typing import Any

from rest_framework import serializers

from apps.audit.action_catalog import (
    CATEGORY_LABELS,
    AuditCategory,
    category_of,
    is_denial,
    label_action,
    label_reason,
)
from apps.audit.entity_labels import EntityKey
from apps.audit.models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer[AuditEvent]):
    """
    Evento com descrições em português. Espera `entity_labels` no contexto
    (resolvidos em lote por `resolve_entity_labels`).
    """

    action_label = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()
    is_denial = serializers.SerializerMethodField()
    reason_label = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    entity_label = serializers.SerializerMethodField()

    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "timestamp",
            "action",
            "action_label",
            "category",
            "category_label",
            "is_denial",
            "reason_label",
            "user",
            "entity_type",
            "entity_id",
            "entity_label",
            "ip_address",
            "metadata",
        )
        read_only_fields = fields

    def get_action_label(self, event: AuditEvent) -> str:
        return label_action(event.action)

    def get_category(self, event: AuditEvent) -> str | None:
        category = category_of(event.action)
        return str(category) if category else None

    def get_category_label(self, event: AuditEvent) -> str | None:
        category = category_of(event.action)
        return CATEGORY_LABELS[category] if category else None

    def get_is_denial(self, event: AuditEvent) -> bool:
        return is_denial(event.action)

    def get_reason_label(self, event: AuditEvent) -> str | None:
        return label_reason(event.metadata.get("reason"))

    def get_user(self, event: AuditEvent) -> dict[str, Any] | None:
        if event.user is None:
            return None
        return {
            "id": str(event.user.pk),
            "username": event.user.username,
            "display_name": event.user.display_name,
            "role_label": event.user.get_role_display(),
        }

    def get_entity_label(self, event: AuditEvent) -> str | None:
        labels: dict[EntityKey, str] = self.context.get("entity_labels", {})
        return labels.get((event.entity_type, event.entity_id))


class AuditEventQuerySerializer(serializers.Serializer[None]):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    user = serializers.UUIDField(required=False)
    category = serializers.ChoiceField(choices=[c.value for c in AuditCategory], required=False)
    action = serializers.CharField(required=False, max_length=64)
    outcome = serializers.ChoiceField(choices=("denied", "granted"), required=False)
    search = serializers.CharField(required=False, allow_blank=True, max_length=100)
    entity_type = serializers.CharField(required=False, max_length=64)
    entity_id = serializers.CharField(required=False, max_length=64)
