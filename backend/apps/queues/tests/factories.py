"""Construção do fluxo recepção → fila clínica com dados fictícios."""

from apps.accounts.models import User
from apps.encounters.models import Encounter
from apps.encounters.services.check_in import check_in_appointment
from apps.patients.tests.factories import create_patient
from apps.professionals.models import Professional, Specialty
from apps.professionals.selectors import get_active_professional_for_user
from apps.professionals.tests.factories import create_professional, create_specialty
from apps.queues.models import QueueEntry, QueueType
from apps.queues.services.forward_to_clinical_queue import forward_to_clinical_queue
from apps.scheduling.tests.factories import create_appointment


def ensure_professional(doctor: User, specialty: Specialty | None = None) -> Professional:
    professional = get_active_professional_for_user(doctor)
    if professional is not None:
        return professional
    specialty = specialty or Specialty.objects.filter(ticket_prefix="GINE").first()
    return create_professional(doctor, specialty or create_specialty())


def check_in_new_patient(
    doctor: User, receptionist: User, patient_name: str = "Paciente Fictício"
) -> Encounter:
    """Agenda um paciente fictício com o médico e faz o check-in."""
    professional = ensure_professional(doctor)
    specialty = professional.specialties.get()
    appointment = create_appointment(
        create_patient(patient_name), professional, specialty, created_by=receptionist
    )
    return check_in_appointment(appointment.id, checked_in_by=receptionist)


def reception_entry_of(encounter: Encounter) -> QueueEntry:
    return QueueEntry.objects.get(encounter=encounter, queue_type=QueueType.RECEPTION)


def place_in_clinical_queue(
    doctor: User, receptionist: User, patient_name: str = "Paciente Fictício"
) -> QueueEntry:
    """Leva um paciente fictício até a fila clínica ativa do médico."""
    encounter = check_in_new_patient(doctor, receptionist, patient_name)
    return forward_to_clinical_queue(reception_entry_of(encounter).id, forwarded_by=receptionist)
