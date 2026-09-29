"""Check-in: confirma a chegada do paciente e abre o atendimento do dia."""

import uuid

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.core.exceptions import ResourceNotFoundError, StateConflictError
from apps.encounters.models import Encounter, EncounterStatus, EncounterStatusChange
from apps.professionals.models import Specialty
from apps.queues.services.enqueue import enqueue_in_reception
from apps.scheduling.models import (
    CHECK_IN_ELIGIBLE_APPOINTMENT_STATUSES,
    Appointment,
    AppointmentStatus,
)


def check_in_appointment(
    appointment_id: uuid.UUID, *, checked_in_by: User, ip_address: str | None = None
) -> Encounter:
    """
    Registra a chegada, gera a senha do dia, cria o atendimento e o coloca na
    fila da recepção.

    Exemplo:
        encounter = check_in_appointment(consulta.id, checked_in_by=atendente)
        encounter.ticket_code  # "GINE01"
    """
    with transaction.atomic():
        appointment = _lock_eligible_appointment(appointment_id)
        encounter = Encounter.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            professional=appointment.professional,
            specialty=appointment.specialty,
            service=appointment.service,
            laterality=appointment.laterality,
            with_sedation=appointment.with_sedation,
            ticket_code=_next_ticket_code(appointment.specialty),
            created_by=checked_in_by,
        )
        EncounterStatusChange.objects.create(
            encounter=encounter,
            new_status=EncounterStatus.CHECK_IN_REALIZADO,
            changed_by=checked_in_by,
        )
        enqueue_in_reception(encounter)
        appointment.status = AppointmentStatus.CHECK_IN_REALIZADO
        appointment.save(update_fields=["status", "updated_at"])
        record_audit_event(
            action=AuditAction.CHECK_IN_CREATED,
            user=checked_in_by,
            entity_type="encounter",
            entity_id=str(encounter.pk),
            ip_address=ip_address,
            metadata={"appointment_id": str(appointment.pk), "ticket_code": encounter.ticket_code},
        )
    return encounter


def _lock_eligible_appointment(appointment_id: uuid.UUID) -> Appointment:
    appointment = (
        Appointment.objects.select_for_update(of=("self",))
        .select_related("patient", "professional", "specialty", "service")
        .filter(pk=appointment_id)
        .first()
    )
    if appointment is None:
        raise ResourceNotFoundError(
            f"Agendamento não encontrado: recebido={appointment_id}.",
            code="appointment_not_found",
        )
    if appointment.status not in CHECK_IN_ELIGIBLE_APPOINTMENT_STATUSES:
        raise StateConflictError(
            f"Check-in indisponível para agendamento com status '{appointment.status}': "
            f"esperado {' ou '.join(CHECK_IN_ELIGIBLE_APPOINTMENT_STATUSES)}.",
            code="appointment_not_eligible_for_check_in",
        )
    return appointment


def _next_ticket_code(specialty: Specialty) -> str:
    # O bloqueio da especialidade serializa check-ins simultâneos da mesma
    # especialidade, evitando duas senhas com o mesmo número.
    Specialty.objects.select_for_update().filter(pk=specialty.pk).first()
    issued_today = Encounter.objects.filter(
        specialty=specialty, service_date=timezone.localdate()
    ).count()
    return f"{specialty.ticket_prefix}{issued_today + 1:02d}"
