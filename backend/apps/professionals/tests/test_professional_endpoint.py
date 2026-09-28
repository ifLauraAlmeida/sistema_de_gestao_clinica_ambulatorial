import pytest

from apps.professionals.tests.factories import create_professional, create_specialty

pytestmark = pytest.mark.django_db

URL = "/api/v1/professionals/"


def test_atendente_lists_active_professionals_with_specialties(client_for, atendente, medico):
    gine = create_specialty()
    create_professional(medico, gine)
    inactive_specialty = create_specialty("Cardiologia", "CARD")
    inactive_specialty.is_active = False
    inactive_specialty.save()
    medico.professional_profile.specialties.add(inactive_specialty)

    response = client_for(atendente).get(URL)

    assert response.status_code == 200
    [professional] = response.json()
    assert professional["name"] == "bruno.medico"
    assert [s["ticket_prefix"] for s in professional["specialties"]] == ["GINE"]


def test_medico_cannot_list_professionals(client_for, medico):
    assert client_for(medico).get(URL).status_code == 403
