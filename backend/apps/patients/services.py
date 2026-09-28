"""Criação e atualização cadastral de pacientes."""

from collections.abc import Mapping
from typing import Any

from django.db import IntegrityError, transaction

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.core.exceptions import StateConflictError
from apps.patients.models import Patient


def create_patient(
    data: Mapping[str, Any], *, created_by: User, ip_address: str | None = None
) -> Patient:
    """
    Cria o cadastro do paciente e registra auditoria.

    Exemplo:
        create_patient({"full_name": "Paciente Fictício", "birth_date": date(1990, 1, 1)},
                       created_by=atendente)
    """
    try:
        with transaction.atomic():
            patient = Patient.objects.create(**data, created_by=created_by)
            record_audit_event(
                action=AuditAction.PATIENT_CREATED,
                user=created_by,
                entity_type="patient",
                entity_id=str(patient.pk),
                ip_address=ip_address,
            )
    except IntegrityError as error:
        raise _duplicate_cpf_error() from error
    return patient


def update_patient_demographics(
    patient: Patient,
    changes: Mapping[str, Any],
    *,
    updated_by: User,
    ip_address: str | None = None,
) -> Patient:
    """
    Atualiza dados cadastrais registrando quais campos mudaram.

    A auditoria guarda apenas os nomes dos campos, não os valores pessoais.

    Exemplo:
        update_patient_demographics(patient, {"phone": "21999990000"}, updated_by=atendente)
    """
    changed_fields = sorted(
        field for field, value in changes.items() if getattr(patient, field) != value
    )
    if not changed_fields:
        return patient

    try:
        with transaction.atomic():
            for field in changed_fields:
                setattr(patient, field, changes[field])
            patient.save(update_fields=[*changed_fields, "updated_at"])
            record_audit_event(
                action=AuditAction.PATIENT_UPDATED,
                user=updated_by,
                entity_type="patient",
                entity_id=str(patient.pk),
                ip_address=ip_address,
                metadata={"changed_fields": ",".join(changed_fields)},
            )
    except IntegrityError as error:
        raise _duplicate_cpf_error() from error
    return patient


def _duplicate_cpf_error() -> StateConflictError:
    return StateConflictError(
        "Já existe um paciente cadastrado com este CPF.", code="patient_duplicate_cpf"
    )
