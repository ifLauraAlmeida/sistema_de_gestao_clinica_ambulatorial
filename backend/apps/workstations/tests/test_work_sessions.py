import pytest

from apps.audit.models import AuditEvent
from apps.workstations.models import WorkSession
from apps.workstations.services import start_work_session
from apps.workstations.tests.factories import create_consultation_room, create_reception_desk

pytestmark = pytest.mark.django_db


@pytest.fixture
def guiche():
    return create_reception_desk("Guichê 04")


@pytest.fixture
def consultorio():
    return create_consultation_room("Consultório 03")


def test_atendente_lists_only_reception_desks(client_for, atendente, guiche, consultorio):
    response = client_for(atendente).get("/api/v1/work-sessions/stations/")

    assert response.status_code == 200
    assert [station["name"] for station in response.json()] == ["Guichê 04"]


def test_medico_lists_only_consultation_rooms(client_for, medico, guiche, consultorio):
    response = client_for(medico).get("/api/v1/work-sessions/stations/")

    assert [station["name"] for station in response.json()] == ["Consultório 03"]


def test_inactive_station_is_not_listed_nor_selectable(client_for, atendente, guiche):
    guiche.is_active = False
    guiche.save()
    client = client_for(atendente)

    assert client.get("/api/v1/work-sessions/stations/").json() == []
    response = client.post("/api/v1/work-sessions/", {"station_id": str(guiche.id)}, format="json")
    assert response.status_code == 404


def test_atendente_selects_reception_desk(client_for, atendente, guiche):
    response = client_for(atendente).post(
        "/api/v1/work-sessions/", {"station_id": str(guiche.id)}, format="json"
    )

    assert response.status_code == 201
    assert response.json()["station"]["name"] == "Guichê 04"
    session = WorkSession.objects.get(user=atendente)
    assert session.station_type == "RECEPTION_DESK"
    assert AuditEvent.objects.filter(action="WORK_SESSION_STARTED", user=atendente).exists()


def test_atendente_cannot_select_consultation_room(client_for, atendente, consultorio):
    response = client_for(atendente).post(
        "/api/v1/work-sessions/", {"station_id": str(consultorio.id)}, format="json"
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "station_type_not_allowed"
    assert not WorkSession.objects.exists()
    assert AuditEvent.objects.filter(action="ACCESS_DENIED", user=atendente).exists()


def test_medico_selects_consultation_room(client_for, medico, consultorio):
    response = client_for(medico).post(
        "/api/v1/work-sessions/", {"station_id": str(consultorio.id)}, format="json"
    )

    assert response.status_code == 201


def test_medico_cannot_select_reception_desk(client_for, medico, guiche):
    response = client_for(medico).post(
        "/api/v1/work-sessions/", {"station_id": str(guiche.id)}, format="json"
    )

    assert response.status_code == 403


def test_switching_station_closes_previous_session(atendente, guiche):
    other_desk = create_reception_desk("Guichê 02")
    first = start_work_session(atendente, guiche.id)

    second = start_work_session(atendente, other_desk.id)

    first.refresh_from_db()
    assert first.ended_at is not None
    assert second.ended_at is None
    assert WorkSession.objects.filter(user=atendente, ended_at__isnull=True).count() == 1


def test_current_session_endpoint_and_end(client_for, atendente, guiche):
    client = client_for(atendente)
    assert client.get("/api/v1/work-sessions/current/").json() == {"work_session": None}

    start_work_session(atendente, guiche.id)
    current = client.get("/api/v1/work-sessions/current/").json()["work_session"]
    assert current["station"]["name"] == "Guichê 04"

    assert client.post("/api/v1/work-sessions/current/end/").status_code == 204
    assert client.get("/api/v1/work-sessions/current/").json() == {"work_session": None}
    assert AuditEvent.objects.filter(action="WORK_SESSION_ENDED").exists()


def test_me_exposes_required_station_type_and_active_session(client_for, atendente, guiche):
    client = client_for(atendente)
    assert client.get("/api/v1/auth/me/").json()["required_station_type"] == "RECEPTION_DESK"
    assert client.get("/api/v1/auth/me/").json()["active_work_session"] is None

    start_work_session(atendente, guiche.id)

    assert client.get("/api/v1/auth/me/").json()["active_work_session"]["station"]["name"] == (
        "Guichê 04"
    )


def test_gestor_is_not_required_to_select_station(client_for, gestor):
    assert client_for(gestor).get("/api/v1/auth/me/").json()["required_station_type"] is None


def test_work_session_endpoints_require_authentication(api_client):
    assert api_client.get("/api/v1/work-sessions/stations/").status_code == 401
    assert api_client.post("/api/v1/work-sessions/", {}, format="json").status_code == 401
