"""Localização do atendimento e verificação do profissional responsável."""

import uuid

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.core.exceptions import AccessDeniedError, ResourceNotFoundError
from apps.encounters.models import Encounter


def get_encounter(encounter_id: uuid.UUID, *, for_update: bool = False) -> Encounter:
    """
    Busca o atendimento (opcionalmente com SELECT FOR UPDATE) ou lança 404.

    Exemplo:
        encounter = get_encounter(encounter_id, for_update=True)
    """
    queryset = Encounter.objects.select_related("professional", "patient", "specialty")
    if for_update:
        queryset = queryset.select_for_update(of=("self",))
    encounter = queryset.filter(pk=encounter_id).first()
    if encounter is None:
        raise ResourceNotFoundError(
            f"Atendimento não encontrado: recebido={encounter_id}.", code="encounter_not_found"
        )
    return encounter


def ensure_responsible_professional(
    encounter: Encounter, user: User, ip_address: str | None
) -> None:
    """
    Garante que o usuário é o profissional do atendimento; caso contrário audita e nega.

    Deve ser chamada fora da transação da operação, para que a auditoria da
    negação não seja desfeita pelo rollback.
    """
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
        "Somente o profissional responsável pode alterar este atendimento.",
        code="encounter_not_owned",
    )
