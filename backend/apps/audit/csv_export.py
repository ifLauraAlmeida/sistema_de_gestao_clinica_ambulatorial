"""Exportação da auditoria em CSV (sem conteúdo clínico)."""

import csv
import io
from collections.abc import Iterable

from django.utils import timezone

from apps.audit.action_catalog import CATEGORY_LABELS, category_of, label_action, label_reason
from apps.audit.entity_labels import resolve_entity_labels
from apps.audit.models import AuditEvent

EXPORT_LIMIT = 10_000
_HEADER = ("Data e hora", "Usuário", "Perfil", "Categoria", "Ação", "Afetado", "Motivo", "IP")


def export_audit_csv(events: Iterable[AuditEvent]) -> str:
    """
    Gera o CSV (separador ";", compatível com planilhas em português).

    Exemplo:
        export_audit_csv(search_audit_events(filtros))
    """
    rows = list(events)[:EXPORT_LIMIT]
    labels = resolve_entity_labels(rows)
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(_HEADER)
    for event in rows:
        category = category_of(event.action)
        writer.writerow(
            (
                timezone.localtime(event.timestamp).strftime("%d/%m/%Y %H:%M:%S"),
                event.user.display_name if event.user else "",
                event.user.get_role_display() if event.user else "",
                CATEGORY_LABELS[category] if category else "",
                label_action(event.action),
                labels.get((event.entity_type, event.entity_id), event.entity_id),
                label_reason(event.metadata.get("reason")) or "",
                event.ip_address or "",
            )
        )
    return buffer.getvalue()
