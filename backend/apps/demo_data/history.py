"""
Histórico fictício de demonstração (meses passados e agenda futura).

Os registros são gravados diretamente com as datas do passado (os serviços
sempre usam o horário atual), respeitando as mesmas constraints do banco.
Somente para desenvolvimento/demonstração: o comando exige DEBUG.
"""

import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.billing.models import HealthInsurer
from apps.catalog.models import LaboratoryExam, Laterality, Service
from apps.demo_data.history_batch import DayBatch
from apps.demo_data.history_encounter import EncounterActors, record_past_encounter
from apps.demo_data.history_records import (
    CANCELLED_RATE,
    FIRST_NAMES,
    GESTOR_USERNAME,
    HISTORY_PATIENT_COUNT,
    LAST_NAMES,
    NO_SHOW_BEFORE_ARRIVAL_RATE,
    PROFESSIONAL_PLANS,
    RECEPTIONISTS,
    ProfessionalPlan,
)
from apps.encounters.models import Encounter
from apps.patients.models import Patient
from apps.scheduling.models import Appointment, AppointmentStatus
from apps.workstations.models import Station, WorkSession

DAYS_PER_MONTH = 30
SUNDAY = 6
SATURDAY = 5
WORKDAY_START = time(7, 45)
WORKDAY_END = time(18, 10)
FIRST_SLOT = time(8, 0)
# Pacientes frequentes voltam mais vezes, formando histórico clínico.
REGULAR_PATIENTS = 25


@dataclass(frozen=True)
class HistorySummary:
    skipped: bool
    days: int = 0
    appointments: int = 0
    encounters: int = 0
    future_appointments: int = 0


@dataclass(frozen=True)
class HistoryContext:
    rng: random.Random
    users: dict[str, User]
    stations: dict[str, Station]
    services: dict[str, Service]
    insurers: list[HealthInsurer]
    laboratory_exams: list[LaboratoryExam]
    patients: list[Patient]


def generate_demo_history(
    months: int = 4, future_days: int = 14, seed: int = 2026
) -> HistorySummary:
    """
    Gera atendimentos dos últimos `months` meses e a agenda dos próximos dias.

    Não repete a geração: se já existe histórico com mais de uma semana, nada é
    feito. Pressupõe `seed_demo_data` executado (usuários, catálogo, postos).

    Exemplo:
        generate_demo_history(months=4)
    """
    today = timezone.localdate()
    if Encounter.objects.filter(service_date__lt=today - timedelta(days=7)).exists():
        return HistorySummary(skipped=True)
    context = _build_context(random.Random(seed))
    past_days = _business_days(today - timedelta(days=months * DAYS_PER_MONTH), today)
    appointments = encounters = generated_days = 0
    for day in past_days:
        if Encounter.objects.filter(service_date=day).exists():
            continue
        batch = _generate_past_day(day, context)
        with transaction.atomic():
            batch.flush()
        generated_days += 1
        appointments += len(batch.appointments)
        encounters += len(batch.encounters)
    future = _generate_future_agenda(today, future_days, context)
    return HistorySummary(False, generated_days, appointments, encounters, future)


def _business_days(start: date, end_exclusive: date) -> list[date]:
    days = (start + timedelta(days=offset) for offset in range((end_exclusive - start).days))
    return [day for day in days if day.weekday() != SUNDAY]


def _build_context(rng: random.Random) -> HistoryContext:
    usernames = [plan.username for plan in PROFESSIONAL_PLANS]
    usernames += [username for username, _ in RECEPTIONISTS] + [GESTOR_USERNAME]
    users = {user.username: user for user in User.objects.filter(username__in=usernames)}
    missing = set(usernames) - set(users)
    if missing:
        raise RuntimeError(
            f"Usuários de demonstração ausentes: {', '.join(sorted(missing))}. "
            "Execute seed_demo_data antes de gerar o histórico."
        )
    return HistoryContext(
        rng=rng,
        users=users,
        stations={station.name: station for station in Station.objects.all()},
        services={
            service.name: service
            for service in Service.objects.select_related(
                "specialty", "form_template"
            ).prefetch_related("form_template__fields")
        },
        insurers=list(HealthInsurer.objects.filter(is_active=True)),
        laboratory_exams=list(LaboratoryExam.objects.filter(is_active=True)),
        patients=_ensure_history_patients(rng),
    )


def _ensure_history_patients(rng: random.Random) -> list[Patient]:
    names = [f"{first} {last}" for first in FIRST_NAMES for last in LAST_NAMES]
    rng.shuffle(names)
    patients = list(Patient.objects.filter(full_name__startswith="Paciente Fictício"))
    for index, name in enumerate(names[:HISTORY_PATIENT_COUNT]):
        patient, _ = Patient.objects.get_or_create(
            full_name=f"{name} (fictício)",
            defaults={
                "birth_date": date(rng.randint(1950, 2020), rng.randint(1, 12), rng.randint(1, 28)),
                # DDD 00 inexistente: nunca coincide com telefone real.
                "phone": f"(00) 9{index:04d}-{rng.randint(1000, 9999)}",
            },
        )
        patients.append(patient)
    return patients


def _pick_patient(context: HistoryContext) -> Patient:
    pool = context.patients
    if context.rng.random() < 0.5:
        return context.rng.choice(pool[:REGULAR_PATIENTS])
    return context.rng.choice(pool)


def _pick_service(plan: ProfessionalPlan, context: HistoryContext) -> Service:
    names = [name for name, _ in plan.services]
    weights = [weight for _, weight in plan.services]
    return context.services[context.rng.choices(names, weights)[0]]


def _local(day: date, moment: time) -> datetime:
    return timezone.make_aware(datetime.combine(day, moment))


def _open_sessions(day: date, batch: DayBatch, context: HistoryContext) -> dict[str, WorkSession]:
    """Uma sessão de trabalho por pessoa no dia, com login e logout auditados."""
    assignments = list(RECEPTIONISTS) + [(p.username, p.station_name) for p in PROFESSIONAL_PLANS]
    sessions: dict[str, WorkSession] = {}
    for username, station_name in assignments:
        user = context.users[username]
        station = context.stations[station_name]
        start = _local(day, WORKDAY_START) + timedelta(minutes=context.rng.randint(0, 20))
        end = _local(day, WORKDAY_END) + timedelta(minutes=context.rng.randint(0, 30))
        session = WorkSession(
            user=user,
            station=station,
            station_type=station.station_type,
            started_at=start,
            ended_at=end,
        )
        sessions[username] = session
        batch.work_sessions.append(session)
        batch.audit(AuditAction.LOGIN_SUCCESS, user, start - timedelta(minutes=1))
        batch.audit(
            AuditAction.WORK_SESSION_STARTED,
            user,
            start,
            entity_type="work_session",
            entity_id=str(session.pk),
            metadata={"station_name": station.name},
        )
        batch.audit(AuditAction.LOGOUT, user, end)
    return sessions


def _generate_past_day(day: date, context: HistoryContext) -> DayBatch:
    batch = DayBatch()
    sessions = _open_sessions(day, batch, context)
    gestor = context.users[GESTOR_USERNAME]
    batch.audit(AuditAction.LOGIN_SUCCESS, gestor, _local(day, time(9, 0)))
    for plan in PROFESSIONAL_PLANS:
        for appointment in _schedule_plan(day, plan, batch, context):
            _resolve_past_appointment(appointment, plan, batch, sessions, context)
    _add_occasional_denials(day, batch, context)
    return batch


def _schedule_plan(
    day: date, plan: ProfessionalPlan, batch: DayBatch, context: HistoryContext
) -> list[Appointment]:
    rng = context.rng
    count = plan.daily_appointments + rng.randint(-1, 1)
    if day.weekday() == SATURDAY:
        count //= 2
    professional = context.users[plan.username].professional_profile
    slot = _local(day, FIRST_SLOT) + timedelta(minutes=rng.choice((0, 15, 30)))
    appointments = []
    for _ in range(max(count, 0)):
        service = _pick_service(plan, context)
        appointment = Appointment(
            patient=_pick_patient(context),
            professional=professional,
            specialty=service.specialty,
            service=service,
            laterality=rng.choice(Laterality.values) if service.requires_laterality else "",
            scheduled_for=slot,
            status=AppointmentStatus.AGENDADO,
            created_by=context.users[rng.choice(RECEPTIONISTS)[0]],
        )
        if service.is_laboratory_collection:
            exams = rng.sample(context.laboratory_exams, rng.randint(2, 6))
            batch.laboratory_links.append((appointment, exams))
        batch.appointments.append(appointment)
        appointments.append(appointment)
        slot += timedelta(minutes=service.duration_minutes + rng.choice((0, 10, 20, 30)))
    return appointments


def _resolve_past_appointment(
    appointment: Appointment,
    plan: ProfessionalPlan,
    batch: DayBatch,
    sessions: dict[str, WorkSession],
    context: HistoryContext,
) -> None:
    roll = context.rng.random()
    if roll < CANCELLED_RATE:
        appointment.status = AppointmentStatus.CANCELADO
        return
    if roll < CANCELLED_RATE + NO_SHOW_BEFORE_ARRIVAL_RATE:
        appointment.status = AppointmentStatus.NAO_COMPARECEU
        return
    appointment.status = AppointmentStatus.CHECK_IN_REALIZADO
    receptionist_name = context.rng.choice(RECEPTIONISTS)[0]
    actors = EncounterActors(
        receptionist=context.users[receptionist_name],
        reception_session=sessions[receptionist_name],
        professional_user=context.users[plan.username],
        professional_session=sessions[plan.username],
        gestor=context.users[GESTOR_USERNAME],
        writes_clinical_notes=plan.writes_clinical_notes,
    )
    record_past_encounter(batch, appointment, actors, context.insurers, context.rng)


def _add_occasional_denials(day: date, batch: DayBatch, context: HistoryContext) -> None:
    """Negações ocasionais realistas: senha digitada errada e prontuário fora da fila."""
    rng = context.rng
    if rng.random() < 0.3:
        batch.audit(
            AuditAction.LOGIN_FAILED,
            None,
            _local(day, time(rng.randint(7, 17), rng.randint(0, 59))),
            metadata={"username": rng.choice(("recepcao.demo", "medico.demo", "admin"))},
        )
    if rng.random() < 0.15 and batch.encounters:
        target = rng.choice(batch.encounters)
        batch.audit(
            AuditAction.MEDICAL_RECORD_VIEW_DENIED,
            context.users["medico.demo"],
            target.checked_in_at + timedelta(minutes=20),
            entity_type="encounter",
            entity_id=str(target.pk),
            metadata={
                "reason": "encounter_of_another_professional",
                "patient_id": str(target.patient_id),
                "operation": "view_medical_record",
            },
        )


def _generate_future_agenda(today: date, future_days: int, context: HistoryContext) -> int:
    """Agenda dos próximos dias (agendados e alguns confirmados), sem atendimentos."""
    total = 0
    for day in _business_days(today + timedelta(days=1), today + timedelta(days=future_days + 1)):
        if Appointment.objects.filter(scheduled_for__date=day).exists():
            continue
        batch = DayBatch()
        for plan in PROFESSIONAL_PLANS:
            for appointment in _schedule_plan(day, plan, batch, context):
                if context.rng.random() < 0.4:
                    appointment.status = AppointmentStatus.CONFIRMADO
        with transaction.atomic():
            batch.flush()
        total += len(batch.appointments)
    return total
