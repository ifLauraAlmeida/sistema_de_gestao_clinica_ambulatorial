import pytest
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.patients.tests.factories import create_patient
from apps.professionals.tests.factories import create_professional, create_specialty
from apps.scheduling.models import Appointment
from apps.scheduling.tests.factories import create_appointment

pytestmark = pytest.mark.django_db

URL = "/api/v1/appointments/"


@pytest.fixture
def agenda_context(medico, atendente):
    gine = create_specialty()
    return {
        "patient": create_patient(),
        "professional": create_professional(medico, gine),
        "specialty": gine,
    }


def _payload(ctx, **overrides):
    payload = {
        "patient": str(ctx["patient"].id),
        "professional": str(ctx["professional"].id),
        "specialty": str(ctx["specialty"].id),
        "scheduled_for": timezone.now().isoformat(),
    }
    payload.update(overrides)
    return payload


def test_atendente_creates_appointment(client_for, atendente, agenda_context):
    response = client_for(atendente).post(URL, _payload(agenda_context), format="json")

    assert response.status_code == 201
    assert response.json()["status"] == "AGENDADO"
    assert AuditEvent.objects.filter(action="APPOINTMENT_CREATED").exists()


def test_appointment_requires_specialty_of_professional(client_for, atendente, agenda_context):
    orto = create_specialty("Ortopedia", "ORTO")

    response = client_for(atendente).post(
        URL, _payload(agenda_context, specialty=str(orto.id)), format="json"
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "professional_specialty_mismatch"


def test_atendente_views_day_agenda(client_for, atendente, agenda_context):
    create_appointment(**agenda_context, created_by=atendente)

    response = client_for(atendente).get(URL, {"date": timezone.localdate().isoformat()})

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["patient_name"] == "Paciente Fictício"


def test_atendente_confirms_appointment_and_status_change_is_audited(
    client_for, atendente, agenda_context
):
    appointment = create_appointment(**agenda_context, created_by=atendente)

    response = client_for(atendente).patch(
        f"{URL}{appointment.id}/", {"status": "CONFIRMADO"}, format="json"
    )

    assert response.status_code == 200
    event = AuditEvent.objects.get(action="APPOINTMENT_UPDATED")
    assert event.metadata["previous_status"] == "AGENDADO"
    assert event.metadata["new_status"] == "CONFIRMADO"


def test_check_in_status_cannot_be_set_manually(client_for, atendente, agenda_context):
    appointment = create_appointment(**agenda_context, created_by=atendente)

    response = client_for(atendente).patch(
        f"{URL}{appointment.id}/", {"status": "CHECK_IN_REALIZADO"}, format="json"
    )

    assert response.status_code == 400
    appointment.refresh_from_db()
    assert appointment.status == "AGENDADO"


def test_medico_has_no_agenda_access_yet(client_for, medico, agenda_context):
    assert client_for(medico).get(URL).status_code == 403


def test_gestor_views_agenda(client_for, gestor):
    assert client_for(gestor).get(URL).status_code == 200


def test_invalid_date_filter_is_rejected(client_for, atendente):
    response = client_for(atendente).get(URL, {"date": "28-09-2026"})

    assert response.status_code == 400
    assert Appointment.objects.count() == 0


def test_agenda_filters_by_professional_specialty_and_patient(
    client_for, atendente, outro_medico, agenda_context
):
    create_appointment(**agenda_context, created_by=atendente)
    orto = create_specialty("Ortopedia", "ORTO")
    other = create_professional(outro_medico, orto)
    create_appointment(create_patient("Outro Paciente"), other, orto, created_by=atendente)
    client = client_for(atendente)

    by_professional = client.get(URL, {"professional": str(other.id)}).json()
    by_specialty = client.get(URL, {"specialty": str(agenda_context["specialty"].id)}).json()
    by_patient = client.get(URL, {"search": "outro pac"}).json()

    assert [a["patient_name"] for a in by_professional] == ["Outro Paciente"]
    assert [a["patient_name"] for a in by_specialty] == ["Paciente Fictício"]
    assert [a["patient_name"] for a in by_patient] == ["Outro Paciente"]


def test_agenda_shows_ticket_after_check_in(client_for, atendente, agenda_context):
    appointment = create_appointment(**agenda_context, created_by=atendente)
    client = client_for(atendente)
    assert client.get(URL).json()[0]["ticket_code"] is None

    client.post("/api/v1/check-ins/", {"appointment_id": str(appointment.id)}, format="json")

    assert client.get(URL).json()[0]["ticket_code"] == "GINE01"
