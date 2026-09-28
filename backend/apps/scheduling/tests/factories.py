from datetime import datetime

from django.utils import timezone

from apps.accounts.models import User
from apps.patients.models import Patient
from apps.professionals.models import Professional, Specialty
from apps.scheduling.models import Appointment


def create_appointment(
    patient: Patient,
    professional: Professional,
    specialty: Specialty,
    created_by: User,
    scheduled_for: datetime | None = None,
) -> Appointment:
    return Appointment.objects.create(
        patient=patient,
        professional=professional,
        specialty=specialty,
        created_by=created_by,
        scheduled_for=scheduled_for or timezone.now(),
    )
