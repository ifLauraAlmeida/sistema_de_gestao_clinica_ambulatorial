"""Finalização do atendimento pelo médico responsável (status ATENDIDO)."""

import uuid

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.core.exceptions import AccessDeniedError, ResourceNotFoundError
from apps.encounters.models import Encounter, EncounterStatus
from apps.encounters.services.status_transitions import change_encounter_status
from apps.queues.services.finish_clinical_entry import finish_clinical_queue_entry


def complete_encounter(
    encounter_id: uuid.UUID, *, completed_by: User, ip_address: str | None = None
) -> Encounter:
    """
    Marca o atendimento como ATENDIDO e o move para a fila inativa.

    Os registros (paciente, profissional, especialidade, horários, chamadas e
    evoluções) são preservados. A partir daqui o vínculo deste atendimento deixa
    de autorizar acesso clínico ao paciente.

    Exemplo:
        complete_encounter(atendimento.id, completed_by=medico)
    """
    # Verificado fora da transação: a auditoria da negação precisa persistir.
    _ensure_responsible_professional(_get_encounter(encounter_id), completed_by, ip_address)

    with transaction.atomic():
        encounter = _get_encounter(encounter_id, for_update=True)
        previous_status = encounter.status
        encounter.completed_at = timezone.now()
        encounter.save(update_fields=["completed_at"])
        change_encounter_status(
            encounter, EncounterStatus.ATENDIDO, changed_by=completed_by, ip_address=ip_address
        )
        finish_clinical_queue_entry(encounter)
        record_audit_event(
            action=AuditAction.ENCOUNTER_COMPLETED,
            user=completed_by,
            entity_type="encounter",
            entity_id=str(encounter.pk),
            ip_address=ip_address,
            metadata={"previous_status": previous_status, "new_status": encounter.status},
        )
    return encounter


def _get_encounter(encounter_id: uuid.UUID, *, for_update: bool = False) -> Encounter:
    queryset = Encounter.objects.select_related("professional", "patient", "specialty")
    if for_update:
        queryset = queryset.select_for_update(of=("self",))
    encounter = queryset.filter(pk=encounter_id).first()
    if encounter is None:
        raise ResourceNotFoundError(
            f"Atendimento não encontrado: recebido={encounter_id}.", code="encounter_not_found"
        )
    return encounter


def _ensure_responsible_professional(
    encounter: Encounter, user: User, ip_address: str | None
) -> None:
    if encounter.professional.user_id == user.pk:
        return
    record_audit_event(
        action=AuditAction.ACCESS_DENIED,
        user=user,
        entity_type="encounter",
        entity_id=str(encounter.pk),
        ip_address=ip_address,
        metadata={"reason": "not_responsible_professional"},
    )
    raise AccessDeniedError(
        "Somente o profissional responsável pode finalizar este atendimento.",
        code="encounter_not_owned",
    )
