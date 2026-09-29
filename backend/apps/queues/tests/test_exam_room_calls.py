import pytest

from apps.accounts.models import UserRole
from apps.accounts.tests.factories import create_user
from apps.professionals.tests.factories import create_professional, create_specialty
from apps.queues.tests.factories import place_in_clinical_queue
from apps.workstations.models import Station, StationType
from apps.workstations.services import start_work_session
from apps.workstations.tests.factories import create_consultation_room

pytestmark = pytest.mark.django_db


@pytest.fixture
def tecnico(db):
    user = create_user("tecnico.rx", UserRole.TECNICO)
    create_professional(user, create_specialty("Radiologia", "RX"))
    return user


@pytest.fixture
def sala_raio_x():
    return Station.objects.create(station_type=StationType.EXAM_ROOM, name="Sala de Raio-X")


def test_tecnico_opens_session_only_in_exam_room(client_for, tecnico, sala_raio_x):
    client = client_for(tecnico)

    stations = client.get("/api/v1/work-sessions/stations/").json()
    room = create_consultation_room()

    assert [station["name"] for station in stations] == ["Sala de Raio-X"]
    assert client.get("/api/v1/auth/me/").json()["required_station_type"] == "EXAM_ROOM"
    denied = client.post("/api/v1/work-sessions/", {"station_id": str(room.id)}, format="json")
    assert denied.status_code == 403


def test_tecnico_calls_own_patient_to_exam_room(client_for, tecnico, atendente, sala_raio_x):
    entry = place_in_clinical_queue(tecnico, atendente, "Paciente do Raio-X")
    start_work_session(tecnico, sala_raio_x.id)

    response = client_for(tecnico).post(f"/api/v1/clinical-queue/{entry.id}/call/")

    assert response.status_code == 201
    assert response.json()["destination_label"] == "Sala de Raio-X"
    assert response.json()["destination_type"] == "EXAM_ROOM"


def test_tecnico_cannot_open_medical_record(client_for, tecnico, atendente):
    entry = place_in_clinical_queue(tecnico, atendente)

    response = client_for(tecnico).get(f"/api/v1/encounters/{entry.encounter_id}/medical-record/")

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "medical_record_access_denied"
