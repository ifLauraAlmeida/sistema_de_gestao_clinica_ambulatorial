"""Consultas de eventos de auditoria."""

from django.db.models import QuerySet

from apps.audit.models import AuditEvent


def search_audit_events(
    *, action: str | None = None, entity_type: str | None = None, entity_id: str | None = None
) -> QuerySet[AuditEvent]:
    """
    Eventos de auditoria filtrados, do mais recente ao mais antigo.

    Exemplo:
        search_audit_events(action="MEDICAL_RECORD_VIEW_DENIED")
    """
    queryset = AuditEvent.objects.select_related("user").order_by("-timestamp")
    if action:
        queryset = queryset.filter(action=action)
    if entity_type:
        queryset = queryset.filter(entity_type=entity_type)
    if entity_id:
        queryset = queryset.filter(entity_id=entity_id)
    return queryset
