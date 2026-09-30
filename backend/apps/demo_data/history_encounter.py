"""Ciclo de vida fictício de um atendimento passado, com horários coerentes."""

import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.billing.models import (
    BillingStatus,
    EncounterBilling,
    HealthInsurer,
    PayerType,
    PaymentMethod,
)
from apps.demo_data.history_batch import DayBatch
from apps.demo_data.history_records import (
    CLINICAL_NOTES,
    INSURANCE_RATE,
    NO_SHOW_AFTER_CALL_RATE,
    PENDING_PAYMENT_RATE,
)
from apps.demo_data.history_values import fake_field_value
from apps.encounters.models import Encounter, EncounterStatus, EncounterStatusChange
from apps.medical_records.models import ClinicalNote
from apps.procedures.models import ProcedureRecord
from apps.queues.models import QueueCall, QueueEntry, QueueEntryStatus, QueueType
from apps.scheduling.models import Appointment
from apps.workstations.models import WorkSession

S = EncounterStatus


@dataclass(frozen=True)
class EncounterActors:
    receptionist: User
    reception_session: WorkSession
    professional_user: User
    professional_session: WorkSession
    gestor: User
    writes_clinical_notes: bool


@dataclass(frozen=True)
class Timeline:
    checked_in: datetime
    reception_call: datetime
    forwarded: datetime
    clinical_call: datetime
    started: datetime
    completed: datetime


def build_timeline(scheduled: datetime, duration: int, rng: random.Random) -> Timeline:
    """Horários de cada etapa a partir do horário agendado."""
    checked_in = scheduled - timedelta(minutes=rng.randint(5, 25))
    reception_call = checked_in + timedelta(minutes=rng.randint(1, 12))
    forwarded = reception_call + timedelta(minutes=rng.randint(2, 6))
    clinical_call = max(forwarded + timedelta(minutes=rng.randint(3, 45)), scheduled)
    started = clinical_call + timedelta(minutes=rng.randint(1, 4))
    completed = started + timedelta(minutes=max(5, duration + rng.randint(-5, 10)))
    return Timeline(checked_in, reception_call, forwarded, clinical_call, started, completed)


def record_past_encounter(
    batch: DayBatch,
    appointment: Appointment,
    actors: EncounterActors,
    insurers: list[HealthInsurer],
    rng: random.Random,
) -> None:
    """
    Registra check-in, filas, chamadas, execução, desfecho, financeiro e
    auditoria de um agendamento passado em que o paciente compareceu.
    """
    service = appointment.service
    assert service is not None
    timeline = build_timeline(appointment.scheduled_for, service.duration_minutes, rng)
    no_show = rng.random() < NO_SHOW_AFTER_CALL_RATE
    encounter = Encounter(
        patient=appointment.patient,
        appointment=appointment,
        professional=appointment.professional,
        specialty=appointment.specialty,
        service=service,
        laterality=appointment.laterality,
        ticket_code=batch.next_ticket(service.specialty.ticket_prefix),
        service_date=appointment.scheduled_for.date(),
        status=S.NAO_COMPARECEU if no_show else S.ATENDIDO,
        checked_in_at=timeline.checked_in,
        completed_at=None if no_show else timeline.completed,
        created_by=actors.receptionist,
    )
    batch.encounters.append(encounter)
    _record_status_history(batch, encounter, actors, timeline, no_show)
    _record_queues_and_calls(batch, encounter, actors, timeline, no_show)
    _record_audit_trail(batch, encounter, actors, timeline, no_show)
    if not no_show:
        _record_clinical_work(batch, encounter, actors, timeline, rng)
    _record_billing(batch, encounter, actors, insurers, timeline, rng)


def _record_status_history(
    batch: DayBatch, encounter: Encounter, actors: EncounterActors, t: Timeline, no_show: bool
) -> None:
    steps: list[tuple[str, str, User, datetime]] = [
        ("", S.CHECK_IN_REALIZADO, actors.receptionist, t.checked_in),
        (S.CHECK_IN_REALIZADO, S.AGUARDANDO_PROFISSIONAL, actors.receptionist, t.forwarded),
        (S.AGUARDANDO_PROFISSIONAL, S.CHAMADO, actors.professional_user, t.clinical_call),
    ]
    if no_show:
        steps.append((S.CHAMADO, S.NAO_COMPARECEU, actors.professional_user, t.started))
    else:
        steps.append((S.CHAMADO, S.EM_ATENDIMENTO, actors.professional_user, t.started))
        steps.append((S.EM_ATENDIMENTO, S.ATENDIDO, actors.professional_user, t.completed))
    batch.status_changes += [
        EncounterStatusChange(
            encounter=encounter,
            previous_status=previous,
            new_status=new,
            changed_by=user,
            changed_at=at,
        )
        for previous, new, user, at in steps
    ]


def _record_queues_and_calls(
    batch: DayBatch, encounter: Encounter, actors: EncounterActors, t: Timeline, no_show: bool
) -> None:
    reception = QueueEntry(
        encounter=encounter,
        queue_type=QueueType.RECEPTION,
        status=QueueEntryStatus.FINISHED,
        entered_at=t.checked_in,
        finished_at=t.forwarded,
    )
    clinical = QueueEntry(
        encounter=encounter,
        queue_type=QueueType.CLINICAL,
        professional=encounter.professional,
        status=QueueEntryStatus.NO_SHOW if no_show else QueueEntryStatus.FINISHED,
        entered_at=t.forwarded,
        finished_at=t.started if no_show else t.completed,
    )
    batch.queue_entries += [reception, clinical]
    batch.calls.append(
        _call(reception, actors.receptionist, actors.reception_session, t.reception_call, 1)
    )
    batch.calls.append(
        _call(clinical, actors.professional_user, actors.professional_session, t.clinical_call, 1)
    )
    if no_show:
        recall_at = t.clinical_call + timedelta(minutes=3)
        batch.calls.append(
            _call(clinical, actors.professional_user, actors.professional_session, recall_at, 2)
        )


def _call(
    entry: QueueEntry, user: User, session: WorkSession, at: datetime, attempt: int
) -> QueueCall:
    return QueueCall(
        queue_entry=entry,
        called_by=user,
        work_session=session,
        destination_type=session.station.station_type,
        destination_id=session.station.pk,
        destination_label=session.station.name,
        attempt_number=attempt,
        called_at=at,
    )


def _record_audit_trail(
    batch: DayBatch, encounter: Encounter, actors: EncounterActors, t: Timeline, no_show: bool
) -> None:
    encounter_id = str(encounter.pk)
    ticket = {"ticket_code": encounter.ticket_code}
    batch.audit(
        AuditAction.CHECK_IN_CREATED,
        actors.receptionist,
        t.checked_in,
        entity_type="encounter",
        entity_id=encounter_id,
        metadata=ticket,
    )
    batch.audit(
        AuditAction.QUEUE_TICKET_CALLED,
        actors.receptionist,
        t.reception_call,
        metadata={**ticket, "destination_label": actors.reception_session.station.name},
    )
    batch.audit(
        AuditAction.QUEUE_ENTRY_FORWARDED, actors.receptionist, t.forwarded, metadata=ticket
    )
    batch.audit(
        AuditAction.QUEUE_TICKET_CALLED,
        actors.professional_user,
        t.clinical_call,
        metadata={**ticket, "destination_label": actors.professional_session.station.name},
    )
    if no_show:
        batch.audit(
            AuditAction.QUEUE_ENTRY_NO_SHOW,
            actors.professional_user,
            t.started,
            entity_type="encounter",
            entity_id=encounter_id,
            metadata=ticket,
        )
        return
    batch.audit(
        AuditAction.ENCOUNTER_STARTED,
        actors.professional_user,
        t.started,
        entity_type="encounter",
        entity_id=encounter_id,
    )
    batch.audit(
        AuditAction.ENCOUNTER_COMPLETED,
        actors.professional_user,
        t.completed,
        entity_type="encounter",
        entity_id=encounter_id,
        metadata={"previous_status": S.EM_ATENDIMENTO, "new_status": S.ATENDIDO},
    )


def _record_clinical_work(
    batch: DayBatch, encounter: Encounter, actors: EncounterActors, t: Timeline, rng: random.Random
) -> None:
    user = actors.professional_user
    encounter_id = str(encounter.pk)
    patient = {"patient_id": str(encounter.patient_id)}
    if actors.writes_clinical_notes:
        batch.audit(
            AuditAction.MEDICAL_RECORD_VIEW_GRANTED,
            user,
            t.started,
            entity_type="encounter",
            entity_id=encounter_id,
            metadata={
                **patient,
                "reason": "active_queue_encounter",
                "operation": "view_medical_record",
            },
        )
        note = ClinicalNote(
            encounter=encounter,
            patient=encounter.patient,
            author=user,
            content=rng.choice(CLINICAL_NOTES),
            created_at=t.completed - timedelta(minutes=2),
        )
        batch.notes.append(note)
        batch.audit(
            AuditAction.CLINICAL_NOTE_CREATED,
            user,
            note.created_at,
            entity_type="clinical_note",
            entity_id=str(note.pk),
            metadata={"encounter_id": str(encounter.pk)},
        )
    template = encounter.service.form_template if encounter.service else None
    if template is None:
        return
    values = {field.key: fake_field_value(field, rng) for field in template.fields.all()}
    record = ProcedureRecord(
        encounter=encounter,
        template=template,
        values=values,
        recorded_by=user,
        recorded_at=t.completed - timedelta(minutes=1),
    )
    batch.procedures.append(record)
    batch.audit(
        AuditAction.PROCEDURE_RECORD_SAVED,
        user,
        record.recorded_at,
        entity_type="procedure_record",
        entity_id=str(record.pk),
        metadata={"encounter_id": str(encounter.pk), "template": template.name},
    )


def _record_billing(
    batch: DayBatch,
    encounter: Encounter,
    actors: EncounterActors,
    insurers: list[HealthInsurer],
    t: Timeline,
    rng: random.Random,
) -> None:
    if rng.random() < PENDING_PAYMENT_RATE:
        return
    amount = (encounter.service.reference_price if encounter.service else None) or Decimal("100.00")
    settled_at = t.checked_in + timedelta(minutes=rng.randint(2, 15))
    use_insurance = bool(insurers) and rng.random() < INSURANCE_RATE
    billing = EncounterBilling(
        encounter=encounter,
        payer_type=PayerType.CONVENIO if use_insurance else PayerType.PARTICULAR,
        insurer=rng.choice(insurers) if use_insurance else None,
        guide_number=str(rng.randint(1_000_000, 9_999_999)) if use_insurance else "",
        payment_method="" if use_insurance else rng.choice(PaymentMethod.values),
        amount=amount,
        status=BillingStatus.LIBERADO if use_insurance else BillingStatus.PAGO,
        settled_at=settled_at,
        updated_by=actors.gestor,
    )
    batch.billings.append(billing)
    batch.audit(
        AuditAction.BILLING_AUTHORIZATION_RELEASED
        if use_insurance
        else AuditAction.BILLING_PAYMENT_CONFIRMED,
        actors.gestor,
        settled_at,
        entity_type="encounter",
        entity_id=str(encounter.pk),
        metadata={
            "previous_status": BillingStatus.PENDENTE,
            "new_status": billing.status,
            "previous_amount": None,
            "new_amount": str(amount),
        },
    )
