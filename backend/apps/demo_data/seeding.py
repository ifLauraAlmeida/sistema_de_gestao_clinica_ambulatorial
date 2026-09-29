"""Criação idempotente do cenário de demonstração."""

from datetime import date, datetime, time, timedelta

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.catalog.catalog_loader import load_service_catalog
from apps.catalog.models import LaboratoryExam, Service
from apps.demo_data.fictitious_records import (
    DEMO_PATIENTS,
    DEMO_STATIONS,
    DEMO_TODAY_AGENDA,
    DEMO_USERS,
    DemoUser,
)
from apps.encounters.services.check_in import check_in_appointment
from apps.patients.models import Patient
from apps.professionals.models import Professional, Specialty
from apps.queues.models import QueueEntry, QueueType
from apps.queues.services.forward_to_clinical_queue import forward_to_clinical_queue
from apps.scheduling.models import Appointment
from apps.scheduling.services import create_appointment
from apps.workstations.models import Station

FIRST_SLOT = time(8, 0)
SLOT_MINUTES = 30
# Dos agendamentos do dia: os primeiros chegam e vão para a fila do profissional,
# os seguintes chegam e aguardam na recepção, e os demais ainda não chegaram.
FORWARDED_COUNT = 4
CHECKED_IN_COUNT = 6


def seed_demo_data(password: str) -> None:
    """
    Carrega o catálogo e cria usuários, postos, pacientes e a agenda fictícia do dia.

    Exemplo:
        seed_demo_data(password="senha-local-de-demonstracao")
    """
    with transaction.atomic():
        load_service_catalog()
        users = {demo.username: _ensure_user(demo, password) for demo in DEMO_USERS}
        for demo in DEMO_USERS:
            if demo.specialty_prefixes:
                _ensure_professional(users[demo.username], demo)
        for station_type, name in DEMO_STATIONS:
            Station.objects.get_or_create(station_type=station_type, name=name)
        patients = [_ensure_patient(*record) for record in DEMO_PATIENTS]
        # A agenda por serviço é criada uma vez por dia.
        today = timezone.localdate()
        if not Appointment.objects.filter(
            scheduled_for__date=today, service__isnull=False
        ).exists():
            _create_todays_flow(today, patients, users)


def _ensure_user(demo: DemoUser, password: str) -> User:
    user, _ = User.objects.get_or_create(
        username=demo.username,
        defaults={"first_name": demo.first_name, "last_name": demo.last_name, "role": demo.role},
    )
    user.first_name, user.last_name, user.role = demo.first_name, demo.last_name, demo.role
    user.set_password(password)
    user.is_staff = user.is_superuser = demo.role == UserRole.GESTOR
    user.save()
    return user


def _ensure_professional(user: User, demo: DemoUser) -> Professional:
    professional, _ = Professional.objects.get_or_create(user=user)
    professional.specialties.set(
        Specialty.objects.filter(ticket_prefix__in=demo.specialty_prefixes)
    )
    return professional


def _ensure_patient(full_name: str, birth_date: date, phone: str) -> Patient:
    patient, _ = Patient.objects.get_or_create(
        full_name=full_name, defaults={"birth_date": birth_date}
    )
    if not patient.phone:
        patient.phone = phone
        patient.save(update_fields=["phone", "updated_at"])
    return patient


def _create_todays_flow(today: date, patients: list[Patient], users: dict[str, User]) -> None:
    receptionist = users["recepcao.demo"]
    start = timezone.make_aware(datetime.combine(today, FIRST_SLOT))
    for index, (patient, demo) in enumerate(zip(patients, DEMO_TODAY_AGENDA, strict=True)):
        appointment = create_appointment(
            {
                "patient": patient,
                "professional": users[demo.professional_username].professional_profile,
                "service": Service.objects.get(name=demo.service_name),
                "laterality": demo.laterality,
                "laboratory_exams": LaboratoryExam.objects.filter(name__in=demo.laboratory_exams),
                "scheduled_for": start + timedelta(minutes=SLOT_MINUTES * index),
            },
            created_by=receptionist,
        )
        if index < CHECKED_IN_COUNT:
            encounter = check_in_appointment(appointment.id, checked_in_by=receptionist)
        if index < FORWARDED_COUNT:
            entry = QueueEntry.objects.get(encounter=encounter, queue_type=QueueType.RECEPTION)
            forward_to_clinical_queue(entry.id, forwarded_by=receptionist)
