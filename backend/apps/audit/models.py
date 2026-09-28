import uuid
from typing import Any, NoReturn

from django.conf import settings
from django.db import models
from django.utils import timezone


class ImmutableAuditEventError(Exception):
    """Eventos de auditoria não podem ser alterados nem removidos."""


class AuditEvent(models.Model):
    """
    Registro imutável de uma ação relevante.

    Imutabilidade garantida em duas camadas: no model (save/delete) e por
    trigger no PostgreSQL (migration 0002), que bloqueia UPDATE e DELETE mesmo
    por consultas em lote.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # PROTECT: usuários são desativados, nunca apagados, para preservar a autoria.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    action = models.CharField(max_length=64)
    entity_type = models.CharField(max_length=64, blank=True, default="")
    entity_id = models.CharField(max_length=64, blank=True, default="")
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "evento de auditoria"
        verbose_name_plural = "eventos de auditoria"
        ordering = ("-timestamp",)
        indexes = [
            models.Index(fields=("-timestamp",), name="audit_event_timestamp_idx"),
            models.Index(fields=("action", "-timestamp"), name="audit_event_action_idx"),
            models.Index(fields=("entity_type", "entity_id"), name="audit_event_entity_idx"),
            models.Index(fields=("user", "-timestamp"), name="audit_event_user_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.entity_type}:{self.entity_id}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ImmutableAuditEventError(f"evento de auditoria {self.pk} não pode ser alterado")
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise ImmutableAuditEventError(f"evento de auditoria {self.pk} não pode ser removido")
