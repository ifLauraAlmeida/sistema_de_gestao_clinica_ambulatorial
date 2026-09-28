"""Criação e alteração de agendamentos."""

from collections.abc import Mapping
from typing import Any

from django.db import transaction

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.core.exceptions import DomainError
from apps.professionals.selectors import professional_attends_specialty
from apps.scheduling.models import Appointment


def create_appointment(
    data: Mapping[str, Any], *, created_by: User, ip_address: str | None = None
) -> Appointment:
    """
    Agenda consulta validando que o profissional atende a especialidade.

    Exemplo:
        create_appointment({"patient": p, "professional": prof, "specialty": gine,
                            "scheduled_for": horario}, created_by=atendente)
    """
    professional = data["professional"]
    specialty = data["specialty"]
    if not professional_attends_specialty(professional, specialty.pk):
        raise DomainError(
            f"O profissional não atende a especialidade informada: recebido='{specialty}'.",
            code="professional_specialty_mismatch",
        )

    with transaction.atomic():
        appointment = Appointment.objects.create(**data, created_by=created_by)
        record_audit_event(
            action=AuditAction.APPOINTMENT_CREATED,
            user=created_by,
            entity_type="appointment",
            entity_id=str(appointment.pk),
            ip_address=ip_address,
        )
    return appointment


def update_appointment(
    appointment: Appointment,
    changes: Mapping[str, Any],
    *,
    updated_by: User,
    ip_address: str | None = None,
) -> Appointment:
    """
    Altera horário, status ou observações, auditando status anterior e novo.

    Exemplo:
        update_appointment(consulta, {"status": "CONFIRMADO"}, updated_by=atendente)
    """
    previous_status = appointment.status
    with transaction.atomic():
        for field, value in changes.items():
            setattr(appointment, field, value)
        appointment.save(update_fields=[*changes.keys(), "updated_at"])
        record_audit_event(
            action=AuditAction.APPOINTMENT_UPDATED,
            user=updated_by,
            entity_type="appointment",
            entity_id=str(appointment.pk),
            ip_address=ip_address,
            metadata={
                "changed_fields": ",".join(sorted(changes)),
                "previous_status": previous_status,
                "new_status": appointment.status,
            },
        )
    return appointment
