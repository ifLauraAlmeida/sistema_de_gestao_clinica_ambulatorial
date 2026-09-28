import pytest

from apps.audit.models import AuditEvent
from apps.queues.models import QueueType
from apps.queues.services.call_ticket import call_queue_ticket
from apps.queues.tests.factories import ensure_professional, place_in_clinical_queue
from apps.workstations.services import start_work_session
from apps.workstations.tests.factories import create_consultation_room

pytestmark = pytest.mark.django_db


@pytest.fixture
def called_entry(medico, atendente):
    entry = place_in_clinical_queue(medico, atendente)
    start_work_session(medico, create_consultation_room().id)
    call_queue_ticket(entry.id, QueueType.CLINICAL, caller=medico)
    return entry


def _start_url(entry):
    return f"/api/v1/encounters/{entry.encounter_id}/start/"


def test_medico_starts_called_encounter_and_patient_stays_in_active_queue(
    client_for, medico, called_entry
):
    client = client_for(medico)

    response = client.post(_start_url(called_entry))

    assert response.status_code == 200
    assert response.json()["status"] == "EM_ATENDIMENTO"
    assert AuditEvent.objects.filter(action="ENCOUNTER_STARTED").exists()
    [active] = client.get("/api/v1/clinical-queue/").json()
    assert active["encounter_status"] == "EM_ATENDIMENTO"
    record_url = f"/api/v1/encounters/{called_entry.encounter_id}/medical-record/"
    assert client.get(record_url).status_code == 200


def test_encounter_must_be_called_before_starting(client_for, medico, atendente):
    entry = place_in_clinical_queue(medico, atendente)

    response = client_for(medico).post(_start_url(entry))

    assert response.status_code == 409


def test_other_doctor_cannot_start_encounter(client_for, outro_medico, called_entry):
    ensure_professional(outro_medico)

    response = client_for(outro_medico).post(_start_url(called_entry))

    assert response.status_code == 403
    assert AuditEvent.objects.filter(action="ACCESS_DENIED", user=outro_medico).exists()


@pytest.mark.parametrize("user_fixture", ["atendente", "gestor"])
def test_non_doctors_cannot_start_encounter(client_for, request, user_fixture, called_entry):
    user = request.getfixturevalue(user_fixture)

    assert client_for(user).post(_start_url(called_entry)).status_code == 403


def test_started_encounter_can_be_completed(client_for, medico, called_entry):
    client = client_for(medico)
    client.post(_start_url(called_entry))

    response = client.post(f"/api/v1/encounters/{called_entry.encounter_id}/complete/")

    assert response.json()["status"] == "ATENDIDO"
