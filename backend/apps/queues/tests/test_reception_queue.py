import pytest

from apps.audit.models import AuditEvent
from apps.queues.models import QueueCall, QueueEntry, QueueType
from apps.queues.tests.factories import check_in_new_patient, reception_entry_of
from apps.workstations.services import start_work_session
from apps.workstations.tests.factories import create_reception_desk

pytestmark = pytest.mark.django_db

QUEUE_URL = "/api/v1/reception-queue/"


def _call_url(entry):
    return f"{QUEUE_URL}{entry.id}/call/"


@pytest.fixture
def reception_entry(medico, atendente):
    return reception_entry_of(check_in_new_patient(medico, atendente))


@pytest.fixture
def guiche_04():
    return create_reception_desk("Guichê 04")


def test_check_in_places_patient_in_reception_queue(client_for, atendente, reception_entry):
    response = client_for(atendente).get(QUEUE_URL)

    assert response.status_code == 200
    [item] = response.json()
    assert item["ticket_code"] == "GINE01"
    assert item["status"] == "WAITING"
    assert item["last_call_destination"] is None


def test_call_requires_reception_desk_session(client_for, atendente, reception_entry):
    response = client_for(atendente).post(_call_url(reception_entry))

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "work_session_required"
    assert not QueueCall.objects.exists()


def test_atendente_calls_ticket_to_own_desk(client_for, atendente, reception_entry, guiche_04):
    start_work_session(atendente, guiche_04.id)

    response = client_for(atendente).post(_call_url(reception_entry))

    assert response.status_code == 201
    assert response.json()["destination_label"] == "Guichê 04"
    call = QueueCall.objects.get()
    assert call.destination_type == "RECEPTION_DESK"
    assert call.destination_id == guiche_04.id
    reception_entry.refresh_from_db()
    assert reception_entry.status == "CALLED"
    assert AuditEvent.objects.filter(action="QUEUE_TICKET_CALLED").exists()


def test_recall_creates_new_attempt(client_for, atendente, reception_entry, guiche_04):
    start_work_session(atendente, guiche_04.id)
    client = client_for(atendente)

    client.post(_call_url(reception_entry))
    response = client.post(_call_url(reception_entry))

    assert response.json()["attempt_number"] == 2
    assert QueueCall.objects.count() == 2


def test_changing_desk_keeps_destination_of_previous_calls(
    client_for, atendente, reception_entry, guiche_04
):
    start_work_session(atendente, guiche_04.id)
    client = client_for(atendente)
    client.post(_call_url(reception_entry))

    start_work_session(atendente, create_reception_desk("Guichê 07").id)
    client.post(_call_url(reception_entry))

    labels = list(QueueCall.objects.order_by("attempt_number").values_list("destination_label"))
    assert labels == [("Guichê 04",), ("Guichê 07",)]


def test_forward_moves_patient_to_professional_queue(client_for, atendente, reception_entry):
    response = client_for(atendente).post(f"{QUEUE_URL}{reception_entry.id}/forward/")

    assert response.status_code == 204
    reception_entry.refresh_from_db()
    assert reception_entry.status == "FINISHED"
    clinical = QueueEntry.objects.get(queue_type=QueueType.CLINICAL)
    assert clinical.status == "WAITING"
    assert clinical.encounter.status == "AGUARDANDO_PROFISSIONAL"
    assert client_for(atendente).get(QUEUE_URL).json() == []


def test_finished_entry_cannot_be_called(client_for, atendente, reception_entry, guiche_04):
    start_work_session(atendente, guiche_04.id)
    client = client_for(atendente)
    client.post(f"{QUEUE_URL}{reception_entry.id}/forward/")

    response = client.post(_call_url(reception_entry))

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "queue_entry_not_active"


def test_recent_calls_lists_destination_snapshot(client_for, atendente, reception_entry, guiche_04):
    start_work_session(atendente, guiche_04.id)
    client = client_for(atendente)
    client.post(_call_url(reception_entry))

    [call] = client.get(f"{QUEUE_URL}calls/").json()

    assert call["ticket_code"] == "GINE01"
    assert call["destination_label"] == "Guichê 04"


def test_medico_cannot_view_or_call_reception_queue(client_for, medico, reception_entry):
    client = client_for(medico)

    assert client.get(QUEUE_URL).status_code == 403
    assert client.post(_call_url(reception_entry)).status_code == 403
    assert client.post(f"{QUEUE_URL}{reception_entry.id}/forward/").status_code == 403
