import pytest

from apps.core.exceptions import StateConflictError
from apps.encounters.models import EncounterStatus
from apps.encounters.services.status_transitions import change_encounter_status
from apps.encounters.tests.factories import create_encounter
from apps.patients.tests.factories import create_patient
from apps.professionals.tests.factories import create_professional, create_specialty

pytestmark = pytest.mark.django_db


@pytest.fixture
def encounter(medico, atendente):
    gine = create_specialty()
    return create_encounter(create_patient(), create_professional(medico, gine), gine, atendente)


def test_valid_transition_records_history(encounter, atendente):
    change_encounter_status(
        encounter, EncounterStatus.AGUARDANDO_PROFISSIONAL, changed_by=atendente
    )

    change = encounter.status_changes.get()
    assert change.previous_status == "CHECK_IN_REALIZADO"
    assert change.new_status == "AGUARDANDO_PROFISSIONAL"
    assert change.changed_by == atendente


def test_invalid_transition_is_rejected_with_expected_values(encounter, atendente):
    with pytest.raises(StateConflictError) as error:
        change_encounter_status(encounter, EncounterStatus.ATENDIDO, changed_by=atendente)

    assert "CHECK_IN_REALIZADO" in error.value.message
    assert "AGUARDANDO_PROFISSIONAL" in error.value.message
