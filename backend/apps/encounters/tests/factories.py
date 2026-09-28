from apps.accounts.models import User
from apps.encounters.models import Encounter, EncounterStatus
from apps.patients.models import Patient
from apps.professionals.models import Professional, Specialty


def create_encounter(
    patient: Patient,
    professional: Professional,
    specialty: Specialty,
    created_by: User,
    *,
    ticket_code: str = "GINE01",
    status: EncounterStatus = EncounterStatus.CHECK_IN_REALIZADO,
) -> Encounter:
    return Encounter.objects.create(
        patient=patient,
        professional=professional,
        specialty=specialty,
        created_by=created_by,
        ticket_code=ticket_code,
        status=status,
    )
