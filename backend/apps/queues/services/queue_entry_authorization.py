"""Autorização para operar uma senha (chamar, rechamar, registrar não comparecimento)."""

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.core.exceptions import AccessDeniedError
from apps.queues.models import QueueEntry
from apps.queues.policies import can_call_queue_entry


def ensure_can_operate_queue_entry(user: User, entry: QueueEntry, ip_address: str | None) -> None:
    """
    Permite operar a senha somente a quem pode chamá-la (fila da recepção ou
    própria fila clínica); caso contrário audita e nega.

    Deve ser chamada fora da transação da operação, para que a auditoria da
    negação não seja desfeita pelo rollback.
    """
    if can_call_queue_entry(user, entry):
        return
    record_audit_event(
        action=AuditAction.ACCESS_DENIED,
        user=user,
        entity_type="queue_entry",
        entity_id=str(entry.pk),
        ip_address=ip_address,
        metadata={"reason": "queue_call_not_allowed", "queue_type": entry.queue_type},
    )
    raise AccessDeniedError(
        "Você não pode operar esta senha: ela não pertence a uma fila sob sua responsabilidade.",
        code="queue_call_not_allowed",
    )
