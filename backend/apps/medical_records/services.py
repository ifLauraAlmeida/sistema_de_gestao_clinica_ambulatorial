"""Acesso auditado ao prontuário e registro de evoluções."""

import uuid
from collections.abc import Callable

from django.db import transaction

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.core.exceptions import AccessDeniedError, ResourceNotFoundError
from apps.encounters.models import Encounter
from apps.medical_records.models import ClinicalNote
from apps.medical_records.policies import (
    AccessDecision,
    evaluate_medical_record_update,
    evaluate_medical_record_view,
)

# Mensagem única para qualquer negação: não revela se o paciente existe nem
# detalhes clínicos. O motivo específico fica apenas na auditoria.
ACCESS_DENIED_MESSAGE = "Acesso ao prontuário não autorizado para este atendimento."


def open_medical_record(
    encounter_id: uuid.UUID, *, user: User, ip_address: str | None = None
) -> Encounter:
    """
    Autoriza a consulta ao prontuário via atendimento e audita o resultado.

    Exemplo:
        encounter = open_medical_record(atendimento.id, user=medico)
    """
    return _authorize(
        encounter_id, user, ip_address, evaluate_medical_record_view, "view_medical_record"
    )


def create_clinical_note(
    encounter_id: uuid.UUID, content: str, *, author: User, ip_address: str | None = None
) -> ClinicalNote:
    """
    Registra evolução no atendimento ativo do médico responsável.

    O conteúdo clínico nunca é copiado para a auditoria.

    Exemplo:
        create_clinical_note(atendimento.id, "Paciente estável.", author=medico)
    """
    encounter = _authorize(
        encounter_id, author, ip_address, evaluate_medical_record_update, "create_clinical_note"
    )
    with transaction.atomic():
        note = ClinicalNote.objects.create(
            encounter=encounter, patient=encounter.patient, author=author, content=content
        )
        record_audit_event(
            action=AuditAction.CLINICAL_NOTE_CREATED,
            user=author,
            entity_type="clinical_note",
            entity_id=str(note.pk),
            ip_address=ip_address,
            metadata={"encounter_id": str(encounter.pk)},
        )
    return note


def _authorize(
    encounter_id: uuid.UUID,
    user: User,
    ip_address: str | None,
    evaluate: Callable[[User, Encounter], AccessDecision],
    operation: str,
) -> Encounter:
    encounter = _get_encounter(encounter_id)
    decision = evaluate(user, encounter)
    record_audit_event(
        action=(
            AuditAction.MEDICAL_RECORD_VIEW_GRANTED
            if decision.granted
            else AuditAction.MEDICAL_RECORD_VIEW_DENIED
        ),
        user=user,
        entity_type="encounter",
        entity_id=str(encounter.pk),
        ip_address=ip_address,
        metadata={
            "operation": operation,
            "reason": decision.reason,
            "patient_id": str(encounter.patient_id),
        },
    )
    if not decision.granted:
        raise AccessDeniedError(ACCESS_DENIED_MESSAGE, code="medical_record_access_denied")
    return encounter


def _get_encounter(encounter_id: uuid.UUID) -> Encounter:
    encounter = (
        Encounter.objects.select_related("patient", "specialty", "professional__user")
        .filter(pk=encounter_id)
        .first()
    )
    if encounter is None:
        raise ResourceNotFoundError(
            f"Atendimento não encontrado: recebido={encounter_id}.", code="encounter_not_found"
        )
    return encounter
