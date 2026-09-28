"""Criação idempotente do cenário de demonstração."""

from datetime import date, datetime, time, timedelta

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.demo_data.fictitious_records import (
    DEMO_CONSULTATION_ROOMS,
    DEMO_DOCTOR_SPECIALTIES,
    DEMO_PATIENTS,
    DEMO_RECEPTION_DESKS,
    DEMO_USERS,
)
from apps.encounters.services.check_in import check_in_appointment
from apps.patients.models import Patient
from apps.professionals.models import Professional, Specialty
from apps.queues.models import QueueEntry, QueueType
from apps.queues.services.forward_to_clinical_queue import forward_to_clinical_queue
from apps.scheduling.models import Appointment
from apps.workstations.models import Station, StationType

FIRST_SLOT = time(8, 0)
SLOT_MINUTES = 30
# Dos agendamentos do dia: os primeiros chegam e vão para a fila do médico, os
# seguintes chegam e aguardam na recepção, e os demais ainda não chegaram.
FORWARDED_COUNT = 3
CHECKED_IN_COUNT = 6


def seed_demo_data(password: str) -> None:
    """
    Cria usuários, postos, especialidades, pacientes e a agenda fictícia do dia.

    Exemplo:
        seed_demo_data(password="senha-local-de-demonstracao")
    """
    with transaction.atomic():
        users = {username: _ensure_user(username, password) for username, *_ in DEMO_USERS}
        _ensure_stations()
        professionals = [_ensure_professional(users[name]) for name in DEMO_DOCTOR_SPECIALTIES]
        patients = [_ensure_patient(name, birth) for name, birth in DEMO_PATIENTS]
        if not Appointment.objects.filter(scheduled_for__date=timezone.localdate()).exists():
            _create_todays_flow(patients, professionals, users["recepcao.demo"])


def _ensure_user(username: str, password: str) -> User:
    _, first_name, last_name, role = next(item for item in DEMO_USERS if item[0] == username)
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={"first_name": first_name, "last_name": last_name, "role": role},
    )
    user.set_password(password)
    user.is_staff = user.is_superuser = role == UserRole.GESTOR
    user.save()
    return user


def _ensure_stations() -> None:
    for name in DEMO_RECEPTION_DESKS:
        Station.objects.get_or_create(station_type=StationType.RECEPTION_DESK, name=name)
    for name in DEMO_CONSULTATION_ROOMS:
        Station.objects.get_or_create(station_type=StationType.CONSULTATION_ROOM, name=name)


def _ensure_professional(user: User) -> Professional:
    specialty_name, prefix = DEMO_DOCTOR_SPECIALTIES[user.username]
    specialty, _ = Specialty.objects.get_or_create(
        ticket_prefix=prefix, defaults={"name": specialty_name}
    )
    professional, _ = Professional.objects.get_or_create(user=user)
    professional.specialties.add(specialty)
    return professional


def _ensure_patient(full_name: str, birth_date: date) -> Patient:
    patient, _ = Patient.objects.get_or_create(
        full_name=full_name, defaults={"birth_date": birth_date}
    )
    return patient


def _create_todays_flow(
    patients: list[Patient], professionals: list[Professional], receptionist: User
) -> None:
    start = timezone.make_aware(datetime.combine(timezone.localdate(), FIRST_SLOT))
    for index, patient in enumerate(patients):
        professional = professionals[index % len(professionals)]
        appointment = Appointment.objects.create(
            patient=patient,
            professional=professional,
            specialty=professional.specialties.get(),
            scheduled_for=start + timedelta(minutes=SLOT_MINUTES * index),
            created_by=receptionist,
        )
        if index < CHECKED_IN_COUNT:
            encounter = check_in_appointment(appointment.id, checked_in_by=receptionist)
        if index < FORWARDED_COUNT:
            entry = QueueEntry.objects.get(encounter=encounter, queue_type=QueueType.RECEPTION)
            forward_to_clinical_queue(entry.id, forwarded_by=receptionist)
