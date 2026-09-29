import pytest

from apps.accounts.models import UserRole
from apps.accounts.tests.factories import create_user
from apps.audit.models import AuditEvent
from apps.catalog.tests.factories import create_form_template, create_service
from apps.encounters.services.complete_encounter import complete_encounter
from apps.procedures.models import ProcedureRecord
from apps.professionals.tests.factories import create_professional, create_specialty
from apps.queues.models import QueueType
from apps.queues.services.call_ticket import call_queue_ticket
from apps.queues.tests.factories import place_in_clinical_queue
from apps.workstations.models import Station, StationType
from apps.workstations.services import start_work_session

pytestmark = pytest.mark.django_db


@pytest.fixture
def tecnico(db):
    user = create_user("tecnico.rx", UserRole.TECNICO)
    create_professional(user, create_specialty("Radiologia", "RX"))
    return user


@pytest.fixture
def knee_x_ray(tecnico):
    return create_service(
        "Raio-X de joelho", requires_laterality=True, form_template=create_form_template()
    )


@pytest.fixture
def entry(tecnico, atendente, knee_x_ray):
    return place_in_clinical_queue(tecnico, atendente, "Paciente do Raio-X", knee_x_ray)


def _url(entry):
    return f"/api/v1/encounters/{entry.encounter_id}/procedure/"


def test_tecnico_sees_what_to_perform_without_clinical_data(client_for, tecnico, entry):
    response = client_for(tecnico).get(_url(entry))

    assert response.status_code == 200
    body = response.json()
    assert body["encounter"]["service_name"] == "Raio-X de joelho"
    assert body["encounter"]["laterality_label"] == "Direita"
    assert body["patient"]["display_name"] == "Paciente do Raio-X"
    assert [field["key"] for field in body["form"]["fields"]] == [
        "incidencias",
        "exposicoes",
        "repeticao",
        "qualidade",
    ]
    assert body["values"] is None
    assert body["can_edit"] is True
    assert "clinical_notes" not in body
    assert AuditEvent.objects.filter(action="PROCEDURE_RECORD_VIEW_GRANTED").exists()


def test_saving_creates_versions_and_keeps_values_out_of_audit(client_for, tecnico, entry):
    client = client_for(tecnico)

    client.put(_url(entry), {"values": {"incidencias": "AP", "exposicoes": "2"}}, format="json")
    response = client.put(
        _url(entry), {"values": {"incidencias": "AP e perfil", "repeticao": True}}, format="json"
    )

    assert response.status_code == 200
    assert response.json()["values"]["incidencias"] == "AP e perfil"
    assert response.json()["recorded_by_name"] == "tecnico.rx"
    assert ProcedureRecord.objects.count() == 2
    event = AuditEvent.objects.filter(action="PROCEDURE_RECORD_SAVED").first()
    assert "AP" not in str(event.metadata)


def test_invalid_values_are_reported_per_field(client_for, tecnico, entry):
    response = client_for(tecnico).put(
        _url(entry), {"values": {"exposicoes": "muitas"}}, format="json"
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "procedure_form_invalid"
    assert set(response.json()["error"]["details"]) == {"incidencias", "exposicoes"}


def test_other_technician_cannot_open_procedure(client_for, entry):
    other = create_user("tecnico.lab", UserRole.TECNICO)
    create_professional(other, create_specialty("Laboratório", "LAB"))

    response = client_for(other).get(_url(entry))

    assert response.status_code == 403
    event = AuditEvent.objects.get(action="PROCEDURE_RECORD_VIEW_DENIED")
    assert event.metadata["reason"] == "encounter_of_another_professional"


def test_completion_revokes_technician_access_but_gestor_can_review(
    client_for, tecnico, gestor, entry
):
    room = Station.objects.create(station_type=StationType.EXAM_ROOM, name="Sala de Raio-X")
    start_work_session(tecnico, room.id)
    call_queue_ticket(entry.id, QueueType.CLINICAL, caller=tecnico)
    client_for(tecnico).put(_url(entry), {"values": {"incidencias": "AP"}}, format="json")
    complete_encounter(entry.encounter_id, completed_by=tecnico)

    assert client_for(tecnico).get(_url(entry)).status_code == 403
    review = client_for(gestor).get(_url(entry))
    assert review.status_code == 200
    assert review.json()["can_edit"] is False
    assert review.json()["values"]["incidencias"] == "AP"
    assert client_for(gestor).put(_url(entry), {"values": {}}, format="json").status_code == 403


def test_atendente_cannot_open_procedure(client_for, atendente, entry):
    assert client_for(atendente).get(_url(entry)).status_code == 403


def test_service_without_form_cannot_be_filled(client_for, medico, atendente):
    consultation = create_service(
        "Consulta de teste",
        specialty=create_specialty(),
        category="Consultas e atendimentos",
        group="Teste",
    )
    create_professional(medico, consultation.specialty)
    entry = place_in_clinical_queue(medico, atendente, service=consultation)

    response = client_for(medico).put(_url(entry), {"values": {}}, format="json")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "procedure_form_not_available"


def test_optional_fields_can_be_sent_empty(client_for, tecnico, entry):
    # Regressão: o formulário envia null para campos opcionais não preenchidos.
    response = client_for(tecnico).put(
        _url(entry),
        {"values": {"incidencias": "AP", "exposicoes": None, "repeticao": None, "qualidade": None}},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["values"]["repeticao"] is None
