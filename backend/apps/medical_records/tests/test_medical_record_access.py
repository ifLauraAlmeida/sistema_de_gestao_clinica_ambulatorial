from datetime import date

import pytest
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.encounters.models import Encounter, EncounterStatus
from apps.encounters.services.complete_encounter import complete_encounter
from apps.medical_records.models import ClinicalNote
from apps.queues.models import QueueType
from apps.queues.services.call_ticket import call_queue_ticket
from apps.queues.tests.factories import check_in_new_patient, place_in_clinical_queue
from apps.workstations.services import start_work_session
from apps.workstations.tests.factories import create_consultation_room

pytestmark = pytest.mark.django_db

SECRET_NOTE = "Conteúdo clínico fictício que não pode vazar."


def _record_url(encounter_id):
    return f"/api/v1/encounters/{encounter_id}/medical-record/"


def _history_url(encounter_id):
    return f"/api/v1/encounters/{encounter_id}/clinical-history/"


def _notes_url(encounter_id):
    return f"/api/v1/encounters/{encounter_id}/clinical-notes/"


@pytest.fixture
def active_entry(medico, atendente):
    return place_in_clinical_queue(medico, atendente, "Paciente Ativo")


@pytest.fixture
def previous_encounter(active_entry, medico):
    current = active_entry.encounter
    previous = Encounter.objects.create(
        patient=current.patient,
        professional=current.professional,
        specialty=current.specialty,
        created_by=medico,
        ticket_code="GINE07",
        service_date=date(2025, 1, 10),
        status=EncounterStatus.ATENDIDO,
        completed_at=timezone.now(),
    )
    ClinicalNote.objects.create(
        encounter=previous, patient=current.patient, author=medico, content=SECRET_NOTE
    )
    return previous


def _denied_reasons():
    return list(
        AuditEvent.objects.filter(action="MEDICAL_RECORD_VIEW_DENIED").values_list(
            "metadata__reason", flat=True
        )
    )


def _finish(entry, medico):
    start_work_session(medico, create_consultation_room("Consultório 04").id)
    call_queue_ticket(entry.id, QueueType.CLINICAL, caller=medico)
    complete_encounter(entry.encounter_id, completed_by=medico)


def test_medico_opens_record_of_patient_in_own_active_queue(client_for, medico, active_entry):
    response = client_for(medico).get(_record_url(active_entry.encounter_id))

    assert response.status_code == 200
    assert response.json()["patient"]["display_name"] == "Paciente Ativo"
    event = AuditEvent.objects.get(action="MEDICAL_RECORD_VIEW_GRANTED")
    assert event.metadata["reason"] == "active_queue_encounter"


def test_medico_reads_clinical_history_of_active_patient(
    client_for, medico, active_entry, previous_encounter
):
    response = client_for(medico).get(_history_url(active_entry.encounter_id))

    assert response.status_code == 200
    [previous] = response.json()
    assert previous["service_date"] == "2025-01-10"
    assert previous["clinical_notes"][0]["content"] == SECRET_NOTE


def test_medico_cannot_open_record_of_another_doctors_patient(
    client_for, medico, outro_medico, atendente, active_entry
):
    other_entry = place_in_clinical_queue(outro_medico, atendente, "Paciente de Outra Médica")

    response = client_for(medico).get(_record_url(other_entry.encounter_id))

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "medical_record_access_denied"
    assert _denied_reasons() == ["encounter_of_another_professional"]


def test_medico_cannot_open_record_before_patient_reaches_clinical_queue(
    client_for, medico, atendente
):
    encounter = check_in_new_patient(medico, atendente)

    response = client_for(medico).get(_record_url(encounter.id))

    assert response.status_code == 403
    assert _denied_reasons() == ["encounter_not_active"]


def test_completing_encounter_revokes_clinical_access_through_it(
    client_for, medico, active_entry, previous_encounter
):
    _finish(active_entry, medico)
    client = client_for(medico)

    record = client.get(_record_url(active_entry.encounter_id))
    history = client.get(_history_url(active_entry.encounter_id))

    assert record.status_code == 403
    assert history.status_code == 403
    assert SECRET_NOTE not in history.content.decode()
    assert _denied_reasons() == ["encounter_not_active", "encounter_not_active"]
    assert ClinicalNote.objects.filter(content=SECRET_NOTE).exists()


def test_atendente_cannot_open_record_or_history(client_for, atendente, active_entry):
    client = client_for(atendente)

    record = client.get(_record_url(active_entry.encounter_id))
    history = client.get(_history_url(active_entry.encounter_id))

    assert record.status_code == 403
    assert history.status_code == 403
    assert _denied_reasons() == ["role_without_clinical_access"] * 2


def test_gestor_opens_record_with_administrative_access(client_for, gestor, active_entry):
    response = client_for(gestor).get(_record_url(active_entry.encounter_id))

    assert response.status_code == 200
    event = AuditEvent.objects.get(action="MEDICAL_RECORD_VIEW_GRANTED")
    assert event.metadata["reason"] == "administrative_access"


def test_medico_registers_clinical_note_without_leaking_content_to_audit(
    client_for, medico, active_entry
):
    response = client_for(medico).post(
        _notes_url(active_entry.encounter_id), {"content": SECRET_NOTE}, format="json"
    )

    assert response.status_code == 201
    note = ClinicalNote.objects.get()
    assert note.author == medico
    assert note.patient_id == active_entry.encounter.patient_id
    event = AuditEvent.objects.get(action="CLINICAL_NOTE_CREATED")
    assert SECRET_NOTE not in str(event.metadata)


def test_clinical_note_is_rejected_after_completion(client_for, medico, active_entry):
    _finish(active_entry, medico)

    response = client_for(medico).post(
        _notes_url(active_entry.encounter_id), {"content": "Nova evolução"}, format="json"
    )

    assert response.status_code == 403
    assert not ClinicalNote.objects.exists()


def test_gestor_does_not_register_clinical_notes(client_for, gestor, active_entry):
    response = client_for(gestor).post(
        _notes_url(active_entry.encounter_id), {"content": "Anotação"}, format="json"
    )

    assert response.status_code == 403


def test_unknown_encounter_returns_404(client_for, medico):
    response = client_for(medico).get(_record_url("00000000-0000-0000-0000-000000000000"))

    assert response.status_code == 404
