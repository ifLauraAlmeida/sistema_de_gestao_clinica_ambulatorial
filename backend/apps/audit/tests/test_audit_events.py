import pytest
from django.db import DatabaseError, transaction
from django.test import RequestFactory

from apps.accounts.models import User, UserRole
from apps.audit.actions import AuditAction
from apps.audit.models import AuditEvent, ImmutableAuditEventError
from apps.audit.services import record_audit_event, record_request_audit_event


@pytest.fixture
def gestor(db):
    return User.objects.create_user(username="gestor.auditoria", role=UserRole.GESTOR)


def test_record_audit_event_persists_who_what_and_metadata(gestor):
    event = record_audit_event(
        action=AuditAction.ENCOUNTER_COMPLETED,
        user=gestor,
        entity_type="encounter",
        entity_id="123",
        metadata={"previous_status": "CHAMADO", "new_status": "ATENDIDO"},
    )

    stored = AuditEvent.objects.get(pk=event.pk)
    assert stored.user == gestor
    assert stored.action == "ENCOUNTER_COMPLETED"
    assert stored.metadata == {"previous_status": "CHAMADO", "new_status": "ATENDIDO"}
    assert stored.timestamp is not None


def test_record_request_audit_event_captures_ip_and_user(gestor):
    request = RequestFactory().get("/", REMOTE_ADDR="10.0.0.7")
    request.user = gestor

    event = record_request_audit_event(request, action=AuditAction.LOGOUT)

    assert event.ip_address == "10.0.0.7"
    assert event.user == gestor


def test_audit_event_cannot_be_changed_through_model(gestor):
    event = record_audit_event(action=AuditAction.LOGOUT, user=gestor)
    event.action = "OUTRA"

    with pytest.raises(ImmutableAuditEventError):
        event.save()
    with pytest.raises(ImmutableAuditEventError):
        event.delete()


def test_database_blocks_bulk_update_and_delete(gestor):
    record_audit_event(action=AuditAction.LOGOUT, user=gestor)

    with pytest.raises(DatabaseError), transaction.atomic():
        AuditEvent.objects.update(action="ADULTERADO")
    with pytest.raises(DatabaseError), transaction.atomic():
        AuditEvent.objects.all().delete()
