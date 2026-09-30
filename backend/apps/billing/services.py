"""Confirmação de pagamento e liberação por autorização de convênio."""

import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.billing.models import (
    BillingStatus,
    EncounterBilling,
    HealthInsurer,
    PayerType,
    PaymentMethod,
)
from apps.core.exceptions import ResourceNotFoundError
from apps.encounters.models import Encounter


def confirm_payment(
    encounter_id: uuid.UUID,
    *,
    insurer: HealthInsurer | None,
    guide_number: str,
    payment_method: PaymentMethod,
    amount: Decimal,
    confirmed_by: User,
    ip_address: str | None = None,
) -> EncounterBilling:
    """
    Registra o pagamento do atendimento (particular ou coparticipação de convênio).

    Exemplo:
        confirm_payment(atendimento.id, insurer=None, guide_number="",
                        payment_method=PaymentMethod.PIX, amount=Decimal("150"),
                        confirmed_by=gestor)
    """
    return _settle(
        encounter_id,
        BillingStatus.PAGO,
        AuditAction.BILLING_PAYMENT_CONFIRMED,
        fields={
            "payer_type": PayerType.CONVENIO if insurer else PayerType.PARTICULAR,
            "insurer": insurer,
            "guide_number": guide_number,
            "payment_method": payment_method,
            "amount": amount,
        },
        user=confirmed_by,
        ip_address=ip_address,
    )


def release_authorization(
    encounter_id: uuid.UUID,
    *,
    insurer: HealthInsurer,
    guide_number: str,
    amount: Decimal,
    released_by: User,
    ip_address: str | None = None,
) -> EncounterBilling:
    """
    Libera o atendimento pela guia autorizada do convênio.

    Exemplo:
        release_authorization(atendimento.id, insurer=convenio, guide_number="9988776",
                              amount=Decimal("420"), released_by=gestor)
    """
    return _settle(
        encounter_id,
        BillingStatus.LIBERADO,
        AuditAction.BILLING_AUTHORIZATION_RELEASED,
        fields={
            "payer_type": PayerType.CONVENIO,
            "insurer": insurer,
            "guide_number": guide_number,
            "payment_method": "",
            "amount": amount,
        },
        user=released_by,
        ip_address=ip_address,
    )


def _settle(
    encounter_id: uuid.UUID,
    status: BillingStatus,
    action: AuditAction,
    *,
    fields: dict[str, object],
    user: User,
    ip_address: str | None,
) -> EncounterBilling:
    with transaction.atomic():
        encounter = _lock_encounter(encounter_id)
        billing = EncounterBilling.objects.select_for_update().filter(encounter=encounter).first()
        previous_status = billing.status if billing else BillingStatus.PENDENTE
        previous_amount = str(billing.amount) if billing else None
        billing = billing or EncounterBilling(encounter=encounter)
        for name, value in fields.items():
            setattr(billing, name, value)
        billing.status = status
        billing.settled_at = timezone.now()
        billing.updated_by = user
        billing.save()
        record_audit_event(
            action=action,
            user=user,
            entity_type="encounter",
            entity_id=str(encounter.pk),
            ip_address=ip_address,
            metadata={
                "previous_status": previous_status,
                "new_status": status,
                "previous_amount": previous_amount,
                "new_amount": str(billing.amount),
            },
        )
    return billing


def _lock_encounter(encounter_id: uuid.UUID) -> Encounter:
    encounter = Encounter.objects.select_for_update().filter(pk=encounter_id).first()
    if encounter is None:
        raise ResourceNotFoundError(
            f"Atendimento não encontrado: recebido={encounter_id}.", code="encounter_not_found"
        )
    return encounter
