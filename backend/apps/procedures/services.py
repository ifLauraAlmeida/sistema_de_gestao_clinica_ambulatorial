"""Consulta auditada e registro da execução de procedimentos."""

import uuid
from collections.abc import Mapping

from django.db import transaction

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.catalog.execution_forms import validate_execution_values
from apps.catalog.models import ExecutionFormTemplate
from apps.core.exceptions import AccessDeniedError, ResourceNotFoundError, StateConflictError
from apps.encounters.models import Encounter
from apps.procedures.models import ProcedureRecord
from apps.procedures.policies import ProcedureAccess, evaluate_procedure_access

ACCESS_DENIED_MESSAGE = "Acesso ao procedimento não autorizado para este atendimento."


def open_procedure(
    encounter_id: uuid.UUID, *, user: User, ip_address: str | None = None
) -> tuple[Encounter, ProcedureAccess]:
    """
    Autoriza a consulta ao procedimento do atendimento e audita o resultado.

    Exemplo:
        encounter, access = open_procedure(atendimento.id, user=tecnico)
    """
    encounter = _get_encounter(encounter_id)
    access = evaluate_procedure_access(user, encounter)
    record_audit_event(
        action=(
            AuditAction.PROCEDURE_RECORD_VIEW_GRANTED
            if access.can_view
            else AuditAction.PROCEDURE_RECORD_VIEW_DENIED
        ),
        user=user,
        entity_type="encounter",
        entity_id=str(encounter.pk),
        ip_address=ip_address,
        metadata={"reason": access.reason},
    )
    if not access.can_view:
        raise AccessDeniedError(ACCESS_DENIED_MESSAGE, code="procedure_access_denied")
    return encounter, access


def save_procedure_record(
    encounter_id: uuid.UUID,
    values: Mapping[str, object],
    *,
    user: User,
    ip_address: str | None = None,
) -> ProcedureRecord:
    """
    Valida os campos do formulário do serviço e grava nova versão do registro.

    Os valores não são copiados para a auditoria.

    Exemplo:
        save_procedure_record(atendimento.id, {"incidencias": "AP e perfil"}, user=tecnico)
    """
    encounter, access = open_procedure(encounter_id, user=user, ip_address=ip_address)
    if not access.can_edit:
        raise AccessDeniedError(ACCESS_DENIED_MESSAGE, code="procedure_access_denied")
    template = _require_template(encounter)
    cleaned = validate_execution_values(template.fields.all(), values)
    with transaction.atomic():
        record = ProcedureRecord.objects.create(
            encounter=encounter, template=template, values=cleaned, recorded_by=user
        )
        record_audit_event(
            action=AuditAction.PROCEDURE_RECORD_SAVED,
            user=user,
            entity_type="procedure_record",
            entity_id=str(record.pk),
            ip_address=ip_address,
            metadata={"encounter_id": str(encounter.pk), "template": template.name},
        )
    return record


def latest_procedure_record(encounter: Encounter) -> ProcedureRecord | None:
    """Versão vigente do registro do procedimento, se houver."""
    return (
        encounter.procedure_records.select_related("recorded_by").order_by("-recorded_at").first()
    )


def _require_template(encounter: Encounter) -> ExecutionFormTemplate:
    template = encounter.service.form_template if encounter.service else None
    if template is None:
        raise StateConflictError(
            "O serviço deste atendimento não possui campos de procedimento para preencher.",
            code="procedure_form_not_available",
        )
    return template


def _get_encounter(encounter_id: uuid.UUID) -> Encounter:
    encounter = (
        Encounter.objects.select_related(
            "patient", "service__form_template", "specialty", "professional__user", "appointment"
        )
        .filter(pk=encounter_id)
        .first()
    )
    if encounter is None:
        raise ResourceNotFoundError(
            f"Atendimento não encontrado: recebido={encounter_id}.", code="encounter_not_found"
        )
    return encounter
