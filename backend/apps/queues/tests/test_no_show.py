import pytest

from apps.audit.models import AuditEvent
from apps.encounters.models import Encounter
from apps.queues.models import QueueType
from apps.queues.services.call_ticket import call_queue_ticket
from apps.queues.tests.factories import (
    check_in_new_patient,
    ensure_professional,
    place_in_clinical_queue,
    reception_entry_of,
)
from apps.workstations.services import start_work_session
from apps.workstations.tests.factories import create_consultation_room, create_reception_desk

pytestmark = pytest.mark.django_db


def _clinical_url(entry):
    return f"/api/v1/clinical-queue/{entry.id}/no-show/"


def _reception_url(entry):
    return f"/api/v1/reception-queue/{entry.id}/no-show/"


@pytest.fixture
def called_clinical_entry(medico, atendente):
    entry = place_in_clinical_queue(medico, atendente)
    start_work_session(medico, create_consultation_room().id)
    call_queue_ticket(entry.id, QueueType.CLINICAL, caller=medico)
    return entry


@pytest.fixture
def called_reception_entry(medico, atendente):
    entry = reception_entry_of(check_in_new_patient(medico, atendente))
    start_work_session(atendente, create_reception_desk().id)
    call_queue_ticket(entry.id, QueueType.RECEPTION, caller=atendente)
    return entry


def test_medico_marks_called_patient_as_no_show(client_for, medico, called_clinical_entry):
    client = client_for(medico)

    response = client.post(_clinical_url(called_clinical_entry))

    assert response.status_code == 200
    assert response.json()["status"] == "NO_SHOW"
    encounter = Encounter.objects.get(pk=called_clinical_entry.encounter_id)
    assert encounter.status == "NAO_COMPARECEU"
    assert client.get("/api/v1/clinical-queue/").json() == []
    [inactive] = client.get("/api/v1/clinical-queue/", {"status": "inactive"}).json()
    assert inactive["encounter_status_label"] == "Não compareceu"
    event = AuditEvent.objects.get(action="QUEUE_ENTRY_NO_SHOW")
    assert event.metadata["call_attempts"] == 1


def test_no_show_revokes_clinical_access(client_for, medico, called_clinical_entry):
    client = client_for(medico)
    client.post(_clinical_url(called_clinical_entry))

    record_url = f"/api/v1/encounters/{called_clinical_entry.encounter_id}/medical-record/"
    assert client.get(record_url).status_code == 403


def test_no_show_is_irreversible(client_for, medico, called_clinical_entry):
    client = client_for(medico)
    client.post(_clinical_url(called_clinical_entry))

    assert client.post(_clinical_url(called_clinical_entry)).status_code == 409
    call_url = f"/api/v1/clinical-queue/{called_clinical_entry.id}/call/"
    assert client.post(call_url).status_code == 409


def test_patient_must_be_called_before_no_show(client_for, medico, atendente):
    entry = place_in_clinical_queue(medico, atendente)

    response = client_for(medico).post(_clinical_url(entry))

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "queue_entry_not_called"


def test_patient_in_consultation_cannot_be_marked_no_show(
    client_for, medico, called_clinical_entry
):
    client = client_for(medico)
    client.post(f"/api/v1/encounters/{called_clinical_entry.encounter_id}/start/")

    assert client.post(_clinical_url(called_clinical_entry)).status_code == 409


def test_other_doctor_cannot_mark_no_show(client_for, outro_medico, called_clinical_entry):
    ensure_professional(outro_medico)

    response = client_for(outro_medico).post(_clinical_url(called_clinical_entry))

    assert response.status_code == 403
    assert AuditEvent.objects.filter(action="ACCESS_DENIED", user=outro_medico).exists()


def test_atendente_marks_reception_no_show(client_for, atendente, called_reception_entry):
    client = client_for(atendente)

    response = client.post(_reception_url(called_reception_entry))

    assert response.status_code == 200
    assert client.get("/api/v1/reception-queue/").json() == []
    encounter = Encounter.objects.get(pk=called_reception_entry.encounter_id)
    assert encounter.status == "NAO_COMPARECEU"


def test_atendente_cannot_mark_clinical_no_show(client_for, atendente, called_clinical_entry):
    assert client_for(atendente).post(_clinical_url(called_clinical_entry)).status_code == 403


def test_medico_cannot_mark_reception_no_show(client_for, medico, called_reception_entry):
    assert client_for(medico).post(_reception_url(called_reception_entry)).status_code == 403
