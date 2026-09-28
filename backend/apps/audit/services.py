"""Registro de eventos de auditoria."""

from collections.abc import Mapping

from django.http import HttpRequest

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.models import AuditEvent
from apps.core.request_metadata import get_client_ip

AuditMetadataValue = str | int | bool | None
AuditMetadata = Mapping[str, AuditMetadataValue]


def record_audit_event(
    *,
    action: AuditAction,
    user: User | None,
    entity_type: str = "",
    entity_id: str = "",
    ip_address: str | None = None,
    metadata: AuditMetadata | None = None,
) -> AuditEvent:
    """
    Grava um evento de auditoria.

    `metadata` deve conter apenas identificadores e estados; nunca senhas,
    tokens, CPF completo ou conteúdo clínico.

    Exemplo:
        record_audit_event(
            action=AuditAction.ENCOUNTER_COMPLETED,
            user=doctor,
            entity_type="encounter",
            entity_id=str(encounter.id),
            metadata={"previous_status": "CHAMADO", "new_status": "ATENDIDO"},
        )
    """
    return AuditEvent.objects.create(
        action=action,
        user=user,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=ip_address,
        metadata=dict(metadata or {}),
    )


def record_request_audit_event(
    request: HttpRequest,
    *,
    action: AuditAction,
    entity_type: str = "",
    entity_id: str = "",
    metadata: AuditMetadata | None = None,
) -> AuditEvent:
    """
    Grava um evento usando o usuário autenticado e o IP da requisição.

    Exemplo:
        record_request_audit_event(request, action=AuditAction.LOGOUT)
    """
    user = request.user if isinstance(request.user, User) else None
    return record_audit_event(
        action=action,
        user=user,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=get_client_ip(request),
        metadata=metadata,
    )
