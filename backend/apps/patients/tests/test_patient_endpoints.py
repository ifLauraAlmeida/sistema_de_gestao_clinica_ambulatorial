import pytest

from apps.audit.models import AuditEvent
from apps.patients.models import Patient
from apps.patients.tests.factories import build_fake_cpf, create_patient

pytestmark = pytest.mark.django_db

URL = "/api/v1/patients/"


def _payload(**overrides):
    payload = {
        "full_name": "Paciente Fictício Um",
        "cpf": build_fake_cpf("100200300"),
        "birth_date": "1985-03-12",
        "phone": "21900000001",
    }
    payload.update(overrides)
    return payload


def test_atendente_creates_patient_and_creation_is_audited(client_for, atendente):
    response = client_for(atendente).post(URL, _payload(), format="json")

    assert response.status_code == 201
    patient = Patient.objects.get()
    assert patient.created_by == atendente
    assert AuditEvent.objects.filter(action="PATIENT_CREATED", entity_id=str(patient.id)).exists()


def test_invalid_cpf_is_rejected_with_expected_format(client_for, atendente):
    response = client_for(atendente).post(URL, _payload(cpf="123.456.789-00"), format="json")

    assert response.status_code == 400
    assert "cpf" in response.json()["error"]["details"]


def test_duplicate_cpf_returns_conflict(client_for, atendente):
    client = client_for(atendente)
    client.post(URL, _payload(), format="json")

    response = client.post(URL, _payload(full_name="Outro Nome"), format="json")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "patient_duplicate_cpf"


def test_list_masks_cpf_and_searches_by_name(client_for, atendente):
    create_patient("Paciente Alfa", cpf=build_fake_cpf("111222333"))
    create_patient("Paciente Beta")

    response = client_for(atendente).get(URL, {"search": "alfa"})

    results = response.json()["results"]
    assert [item["full_name"] for item in results] == ["Paciente Alfa"]
    assert results[0]["cpf_masked"].startswith("***.")


def test_atendente_updates_allowed_demographics(client_for, atendente):
    patient = create_patient(phone="21900000000")

    response = client_for(atendente).patch(
        f"{URL}{patient.id}/", {"phone": "21911112222"}, format="json"
    )

    assert response.status_code == 200
    patient.refresh_from_db()
    assert patient.phone == "21911112222"
    event = AuditEvent.objects.get(action="PATIENT_UPDATED")
    assert event.metadata == {"changed_fields": "phone"}


def test_medico_cannot_browse_or_create_patients(client_for, medico):
    client = client_for(medico)

    assert client.get(URL).status_code == 403
    assert client.post(URL, _payload(), format="json").status_code == 403


def test_gestor_manages_patients(client_for, gestor):
    client = client_for(gestor)

    assert client.post(URL, _payload(), format="json").status_code == 201
    assert client.get(URL).status_code == 200
