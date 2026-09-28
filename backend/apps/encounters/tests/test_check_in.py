import pytest

from apps.audit.models import AuditEvent
from apps.encounters.models import Encounter, EncounterStatusChange
from apps.patients.tests.factories import create_patient
from apps.professionals.tests.factories import create_professional, create_specialty
from apps.scheduling.tests.factories import create_appointment

pytestmark = pytest.mark.django_db

URL = "/api/v1/check-ins/"


@pytest.fixture
def appointment(medico, atendente):
    gine = create_specialty()
    return create_appointment(
        create_patient(), create_professional(medico, gine), gine, created_by=atendente
    )


def test_atendente_checks_in_and_receives_ticket(client_for, atendente, appointment):
    response = client_for(atendente).post(
        URL, {"appointment_id": str(appointment.id)}, format="json"
    )

    assert response.status_code == 201
    assert response.json()["ticket_code"] == "GINE01"
    assert response.json()["status"] == "CHECK_IN_REALIZADO"
    appointment.refresh_from_db()
    assert appointment.status == "CHECK_IN_REALIZADO"
    assert EncounterStatusChange.objects.filter(new_status="CHECK_IN_REALIZADO").exists()
    assert AuditEvent.objects.filter(action="CHECK_IN_CREATED").exists()


def test_ticket_numbers_increase_per_specialty(client_for, atendente, medico, appointment):
    second = create_appointment(
        create_patient("Paciente Dois"),
        appointment.professional,
        appointment.specialty,
        created_by=atendente,
    )
    client = client_for(atendente)

    client.post(URL, {"appointment_id": str(appointment.id)}, format="json")
    response = client.post(URL, {"appointment_id": str(second.id)}, format="json")

    assert response.json()["ticket_code"] == "GINE02"


def test_same_appointment_cannot_be_checked_in_twice(client_for, atendente, appointment):
    client = client_for(atendente)
    client.post(URL, {"appointment_id": str(appointment.id)}, format="json")

    response = client.post(URL, {"appointment_id": str(appointment.id)}, format="json")

    assert response.status_code == 409
    assert Encounter.objects.count() == 1


def test_unknown_appointment_returns_404(client_for, atendente):
    response = client_for(atendente).post(
        URL, {"appointment_id": "00000000-0000-0000-0000-000000000000"}, format="json"
    )

    assert response.status_code == 404


def test_medico_cannot_check_in(client_for, medico, appointment):
    response = client_for(medico).post(URL, {"appointment_id": str(appointment.id)}, format="json")

    assert response.status_code == 403
    assert not Encounter.objects.exists()
