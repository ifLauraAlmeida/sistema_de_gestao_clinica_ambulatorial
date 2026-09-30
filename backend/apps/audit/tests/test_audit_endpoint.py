import pytest

from apps.audit.actions import AuditAction
from apps.audit.models import AuditEvent
from apps.audit.services import record_audit_event
from apps.queues.tests.factories import place_in_clinical_queue

pytestmark = pytest.mark.django_db

URL = "/api/v1/audit/events/"


def test_gestor_lists_events_with_portuguese_labels(client_for, gestor, medico):
    record_audit_event(
        action=AuditAction.MEDICAL_RECORD_VIEW_DENIED,
        user=medico,
        metadata={"reason": "encounter_of_another_professional"},
    )

    response = client_for(gestor).get(URL, {"action": "MEDICAL_RECORD_VIEW_DENIED"})

    assert response.status_code == 200
    [event] = response.json()["results"]
    assert event["action_label"] == "Prontuário negado"
    assert event["category_label"] == "Prontuário e procedimentos"
    assert event["is_denial"] is True
    assert event["reason_label"] == "atendimento de outro profissional"
    assert event["user"]["username"] == "bruno.medico"
    assert event["user"]["role_label"] == "Médico"


def test_filters_by_outcome_category_and_user(client_for, gestor, medico, atendente):
    record_audit_event(action=AuditAction.LOGIN_SUCCESS, user=medico)
    record_audit_event(action=AuditAction.LOGIN_FAILED, user=None, metadata={"username": "x"})
    record_audit_event(action=AuditAction.PATIENT_CREATED, user=atendente)
    client = client_for(gestor)

    denied = client.get(URL, {"outcome": "denied"}).json()["results"]
    registry = client.get(URL, {"category": "REGISTRY"}).json()["results"]
    by_user = client.get(URL, {"user": str(medico.id)}).json()["results"]

    assert [e["action"] for e in denied] == ["LOGIN_FAILED"]
    assert [e["action"] for e in registry] == ["PATIENT_CREATED"]
    assert [e["action"] for e in by_user] == ["LOGIN_SUCCESS"]


def test_search_by_ticket_or_patient_finds_related_events(client_for, gestor, medico, atendente):
    entry = place_in_clinical_queue(medico, atendente, "Paciente Rastreado")
    client_for(medico).get(f"/api/v1/encounters/{entry.encounter_id}/medical-record/")
    client = client_for(gestor)

    by_ticket = client.get(URL, {"search": entry.encounter.ticket_code}).json()["results"]
    by_patient = client.get(URL, {"search": "rastreado"}).json()["results"]

    opened = [e for e in by_ticket if e["action"] == "MEDICAL_RECORD_VIEW_GRANTED"]
    assert opened and "Paciente Rastreado" in opened[0]["entity_label"]
    assert {e["action"] for e in by_patient} >= {"MEDICAL_RECORD_VIEW_GRANTED", "CHECK_IN_CREATED"}


def test_summary_counts_today_and_is_itself_audited(client_for, gestor):
    record_audit_event(action=AuditAction.LOGIN_FAILED, user=None)

    response = client_for(gestor).get("/api/v1/audit/summary/")

    assert response.status_code == 200
    assert response.json()["today"]["failed_logins"] == 1
    assert response.json()["today"]["denied"] == 1
    assert any(c["value"] == "CLINICAL" for c in response.json()["categories"])
    assert AuditEvent.objects.filter(action="AUDIT_VIEWED", user=gestor).exists()


def test_export_csv_is_audited_and_has_no_clinical_content(client_for, gestor, medico):
    record_audit_event(action=AuditAction.CLINICAL_NOTE_CREATED, user=medico)

    response = client_for(gestor).get("/api/v1/audit/events/export/")

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    content = response.content.decode()
    assert content.splitlines()[0].startswith("Data e hora;Usuário")
    assert "Evolução clínica registrada" in content
    assert AuditEvent.objects.filter(action="AUDIT_EXPORTED", user=gestor).exists()


@pytest.mark.parametrize("user_fixture", ["atendente", "medico"])
@pytest.mark.parametrize("url", [URL, "/api/v1/audit/summary/", "/api/v1/audit/events/export/"])
def test_other_roles_cannot_read_audit(client_for, request, user_fixture, url):
    user = request.getfixturevalue(user_fixture)

    assert client_for(user).get(url).status_code == 403
