import pytest

from apps.audit.models import AuditEvent
from apps.encounters.models import Encounter
from apps.professionals.selectors import get_active_professional_for_user
from apps.queues.models import QueueCall
from apps.queues.tests.factories import ensure_professional, place_in_clinical_queue
from apps.workstations.services import start_work_session
from apps.workstations.tests.factories import create_consultation_room, create_reception_desk

pytestmark = pytest.mark.django_db

QUEUE_URL = "/api/v1/clinical-queue/"


def _call_url(entry):
    return f"{QUEUE_URL}{entry.id}/call/"


def _complete_url(entry):
    return f"/api/v1/encounters/{entry.encounter_id}/complete/"


@pytest.fixture
def own_entry(medico, atendente):
    return place_in_clinical_queue(medico, atendente, "Paciente do Médico")


@pytest.fixture
def other_entry(outro_medico, atendente, own_entry):
    return place_in_clinical_queue(outro_medico, atendente, "Paciente de Outra Médica")


@pytest.fixture
def consultorio_03():
    return create_consultation_room("Consultório 03")


def test_medico_sees_only_own_active_queue(client_for, medico, own_entry, other_entry):
    response = client_for(medico).get(QUEUE_URL)

    assert response.status_code == 200
    assert [item["patient_name"] for item in response.json()] == ["Paciente do Médico"]


def test_medico_cannot_request_queue_of_another_doctor(
    client_for, medico, outro_medico, other_entry
):
    other_professional = get_active_professional_for_user(outro_medico)

    response = client_for(medico).get(QUEUE_URL, {"professional_id": str(other_professional.id)})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "clinical_queue_access_denied"
    assert AuditEvent.objects.filter(action="ACCESS_DENIED", user=medico).exists()


def test_call_requires_consultation_room_session(client_for, medico, own_entry):
    response = client_for(medico).post(_call_url(own_entry))

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "work_session_required"


def test_medico_calls_own_patient_to_room(client_for, medico, own_entry, consultorio_03):
    start_work_session(medico, consultorio_03.id)

    response = client_for(medico).post(_call_url(own_entry))

    assert response.status_code == 201
    assert response.json()["destination_label"] == "Consultório 03"
    own_entry.refresh_from_db()
    assert own_entry.encounter.status == "CHAMADO"


def test_medico_cannot_call_patient_of_another_doctor(
    client_for, medico, other_entry, consultorio_03
):
    start_work_session(medico, consultorio_03.id)

    response = client_for(medico).post(_call_url(other_entry))

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "queue_call_not_allowed"
    assert not QueueCall.objects.exists()
    assert AuditEvent.objects.filter(action="ACCESS_DENIED", user=medico).exists()


def test_atendente_cannot_view_or_call_clinical_queue(client_for, atendente, own_entry):
    start_work_session(atendente, create_reception_desk().id)
    client = client_for(atendente)

    assert client.get(QUEUE_URL).status_code == 403
    assert client.post(_call_url(own_entry)).status_code == 403
    assert not QueueCall.objects.exists()


def test_room_change_keeps_destination_of_previous_call(
    client_for, medico, own_entry, consultorio_03
):
    start_work_session(medico, consultorio_03.id)
    client_for(medico).post(_call_url(own_entry))

    start_work_session(medico, create_consultation_room("Consultório 05").id)

    assert QueueCall.objects.get().destination_label == "Consultório 03"


def test_completing_moves_encounter_from_active_to_inactive_queue(
    client_for, medico, own_entry, consultorio_03
):
    start_work_session(medico, consultorio_03.id)
    client = client_for(medico)
    client.post(_call_url(own_entry))

    response = client.post(_complete_url(own_entry))

    assert response.status_code == 200
    assert response.json()["status"] == "ATENDIDO"
    assert client.get(QUEUE_URL).json() == []
    [inactive] = client.get(QUEUE_URL, {"status": "inactive"}).json()
    assert inactive["encounter_status"] == "ATENDIDO"
    assert inactive["last_call_destination"] == "Consultório 03"
    assert AuditEvent.objects.filter(action="ENCOUNTER_COMPLETED").exists()


def test_completed_encounter_keeps_its_historical_link(
    client_for, medico, own_entry, consultorio_03
):
    start_work_session(medico, consultorio_03.id)
    client = client_for(medico)
    client.post(_call_url(own_entry))
    client.post(_complete_url(own_entry))

    encounter = Encounter.objects.get(pk=own_entry.encounter_id)
    assert encounter.patient.full_name == "Paciente do Médico"
    assert encounter.professional.user == medico
    assert encounter.specialty.ticket_prefix == "GINE"
    assert encounter.completed_at is not None
    assert list(encounter.status_changes.values_list("new_status", flat=True)) == [
        "CHECK_IN_REALIZADO",
        "AGUARDANDO_PROFISSIONAL",
        "CHAMADO",
        "ATENDIDO",
    ]


def test_encounter_must_be_called_before_completion(client_for, medico, own_entry):
    response = client_for(medico).post(_complete_url(own_entry))

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "invalid_encounter_transition"


def test_other_doctor_cannot_complete_encounter(client_for, outro_medico, own_entry):
    ensure_professional(outro_medico)

    response = client_for(outro_medico).post(_complete_url(own_entry))

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "encounter_not_owned"


def test_gestor_sees_every_clinical_queue_and_filters(
    client_for, gestor, medico, own_entry, other_entry
):
    client = client_for(gestor)

    assert len(client.get(QUEUE_URL).json()) == 2
    professional = get_active_professional_for_user(medico)
    filtered = client.get(QUEUE_URL, {"professional_id": str(professional.id)}).json()
    assert [item["patient_name"] for item in filtered] == ["Paciente do Médico"]


def test_gestor_calls_any_clinical_ticket_from_a_room(client_for, gestor, own_entry):
    start_work_session(gestor, create_consultation_room("Consultório 09").id)

    response = client_for(gestor).post(_call_url(own_entry))

    assert response.status_code == 201
