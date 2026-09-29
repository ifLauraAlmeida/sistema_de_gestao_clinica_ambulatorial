import pytest
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.accounts.tests.factories import create_user
from apps.catalog.tests.factories import create_laboratory_exam, create_service
from apps.encounters.models import Encounter
from apps.patients.tests.factories import create_patient
from apps.professionals.tests.factories import create_professional, create_specialty
from apps.queues.models import QueueEntry

pytestmark = pytest.mark.django_db

URL = "/api/v1/appointments/"


@pytest.fixture
def tecnico(db):
    return create_user("tecnico.teste", UserRole.TECNICO)


@pytest.fixture
def radiology(tecnico):
    specialty = create_specialty("Radiologia", "RX")
    return create_professional(tecnico, specialty)


@pytest.fixture
def knee_x_ray(radiology):
    return create_service("Raio-X de joelho", requires_laterality=True)


def _post(client, professional, service, **extra):
    payload = {
        "patient": str(create_patient().id),
        "professional": str(professional.id),
        "service": str(service.id),
        "scheduled_for": timezone.now().isoformat(),
        **extra,
    }
    return client.post(URL, payload, format="json")


def test_laterality_is_required_when_service_demands_it(
    client_for, atendente, radiology, knee_x_ray
):
    response = _post(client_for(atendente), radiology, knee_x_ray)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_service_options"
    assert "laterality" in response.json()["error"]["details"]


def test_laterality_is_an_attribute_not_a_separate_service(
    client_for, atendente, radiology, knee_x_ray
):
    response = _post(client_for(atendente), radiology, knee_x_ray, laterality="ESQUERDA")

    assert response.status_code == 201
    assert response.json()["laterality_label"] == "Esquerda"


def test_sedation_only_for_services_that_allow_it(client_for, atendente, radiology, knee_x_ray):
    response = _post(
        client_for(atendente), radiology, knee_x_ray, laterality="DIREITA", with_sedation=True
    )

    assert response.status_code == 400
    assert "with_sedation" in response.json()["error"]["details"]


def test_laboratory_collection_requires_exams_and_summarizes_preparation(
    client_for, atendente, tecnico
):
    lab = create_specialty("Laboratório", "LAB")
    professional = create_professional(create_user("coleta", UserRole.TECNICO), lab)
    collection = create_service(
        "Coleta de exames laboratoriais",
        specialty=lab,
        category="Laboratório",
        group="Coleta",
        is_laboratory_collection=True,
    )
    glucose = create_laboratory_exam("Glicemia de jejum", fasting_hours=8)
    client = client_for(atendente)

    without_exams = _post(client, professional, collection)
    with_exams = _post(client, professional, collection, laboratory_exams=[str(glucose.id)])

    assert without_exams.status_code == 400
    assert with_exams.status_code == 201
    assert with_exams.json()["laboratory_exam_names"] == ["Glicemia de jejum"]
    assert "Jejum de 8 horas" in with_exams.json()["preparation"]


def test_check_in_copies_service_to_encounter_and_queue(
    client_for, atendente, radiology, knee_x_ray
):
    client = client_for(atendente)
    appointment_id = _post(client, radiology, knee_x_ray, laterality="DIREITA").json()["id"]

    response = client.post("/api/v1/check-ins/", {"appointment_id": appointment_id}, format="json")

    assert response.json()["ticket_code"] == "RX01"
    encounter = Encounter.objects.get(pk=response.json()["id"])
    assert encounter.service == knee_x_ray
    assert encounter.laterality == "DIREITA"
    [entry] = client.get("/api/v1/reception-queue/").json()
    assert entry["service_name"] == "Raio-X de joelho"
    assert entry["laterality_label"] == "Direita"
    assert QueueEntry.objects.count() == 1
