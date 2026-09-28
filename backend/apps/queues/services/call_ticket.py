"""Chamada (e rechamada) de senha para guichê ou consultório."""

import uuid

from django.db import transaction

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.core.exceptions import AccessDeniedError, StateConflictError
from apps.encounters.models import EncounterStatus
from apps.encounters.services.status_transitions import change_encounter_status
from apps.queues.models import QueueCall, QueueEntry, QueueEntryStatus, QueueType
from apps.queues.policies import can_call_queue_entry, get_call_station_type
from apps.queues.services.queue_entry_lookup import (
    ensure_entry_is_active,
    find_queue_entry,
    lock_queue_entry,
)
from apps.workstations.models import WorkSession
from apps.workstations.selectors import get_open_work_session_of_type


def call_queue_ticket(
    entry_id: uuid.UUID,
    queue_type: QueueType,
    *,
    caller: User,
    ip_address: str | None = None,
) -> QueueCall:
    """
    Chama a senha para o posto da sessão de trabalho atual do usuário.

    Chamar novamente a mesma senha gera nova tentativa (rechamada). O destino
    é gravado como snapshot do posto no momento da chamada.

    Exemplo:
        call_queue_ticket(entrada.id, QueueType.RECEPTION, caller=atendente)
    """
    _ensure_can_call(caller, find_queue_entry(entry_id, queue_type), ip_address)

    with transaction.atomic():
        entry = lock_queue_entry(entry_id, queue_type)
        ensure_entry_is_active(entry)
        work_session = _require_work_session(caller, entry)
        call = _register_call(entry, caller, work_session)
        _mark_entry_as_called(entry, caller, ip_address)
        record_audit_event(
            action=AuditAction.QUEUE_TICKET_CALLED,
            user=caller,
            entity_type="queue_entry",
            entity_id=str(entry.pk),
            ip_address=ip_address,
            metadata={
                "ticket_code": entry.encounter.ticket_code,
                "destination_label": call.destination_label,
                "attempt_number": call.attempt_number,
            },
        )
    return call


def _ensure_can_call(caller: User, entry: QueueEntry, ip_address: str | None) -> None:
    # Executado fora da transação: a auditoria da negação precisa persistir.
    if can_call_queue_entry(caller, entry):
        return
    record_audit_event(
        action=AuditAction.ACCESS_DENIED,
        user=caller,
        entity_type="queue_entry",
        entity_id=str(entry.pk),
        ip_address=ip_address,
        metadata={"reason": "queue_call_not_allowed", "queue_type": entry.queue_type},
    )
    raise AccessDeniedError(
        "Você não pode chamar esta senha: ela não pertence a uma fila sob sua responsabilidade.",
        code="queue_call_not_allowed",
    )


def _require_work_session(caller: User, entry: QueueEntry) -> WorkSession:
    station_type = get_call_station_type(entry.queue_type)
    session = get_open_work_session_of_type(caller, station_type)
    if session is None:
        raise StateConflictError(
            f"Selecione um posto do tipo '{station_type.label}' antes de chamar pacientes.",
            code="work_session_required",
        )
    return session


def _register_call(entry: QueueEntry, caller: User, work_session: WorkSession) -> QueueCall:
    return QueueCall.objects.create(
        queue_entry=entry,
        called_by=caller,
        work_session=work_session,
        destination_type=work_session.station.station_type,
        destination_id=work_session.station.pk,
        destination_label=work_session.station.name,
        attempt_number=entry.calls.count() + 1,
    )


def _mark_entry_as_called(entry: QueueEntry, caller: User, ip_address: str | None) -> None:
    entry.status = QueueEntryStatus.CALLED
    entry.save(update_fields=["status"])
    encounter = entry.encounter
    if entry.queue_type == QueueType.CLINICAL and encounter.status != EncounterStatus.CHAMADO:
        change_encounter_status(
            encounter, EncounterStatus.CHAMADO, changed_by=caller, ip_address=ip_address
        )
