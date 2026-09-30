"""Consultas do financeiro do dia."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db.models import QuerySet

from apps.billing.models import BillingStatus, EncounterBilling
from apps.encounters.models import Encounter, EncounterStatus


def list_billing_day(day: date) -> QuerySet[Encounter]:
    """
    Atendimentos do dia (check-in realizado, exceto cancelados) com o financeiro.

    Exemplo:
        list_billing_day(timezone.localdate())
    """
    return (
        Encounter.objects.filter(service_date=day)
        .exclude(status=EncounterStatus.CANCELADO)
        .select_related("patient", "service", "specialty", "billing__insurer")
        .order_by("checked_in_at")
    )


def billing_of(encounter: Encounter) -> EncounterBilling | None:
    """Registro financeiro do atendimento, se já houver."""
    try:
        return encounter.billing
    except EncounterBilling.DoesNotExist:
        return None


def expected_amount(encounter: Encounter) -> Decimal | None:
    """Valor registrado ou, na falta dele, o preço de referência do serviço."""
    billing = billing_of(encounter)
    if billing:
        return billing.amount
    return encounter.service.reference_price if encounter.service else None


@dataclass(frozen=True)
class BillingDaySummary:
    paid: int
    pending: int
    released: int
    received_amount: Decimal


def summarize_billing_day(day: date) -> BillingDaySummary:
    """Indicadores do dia: pagos, pendentes, guias liberadas e valor recebido."""
    encounters = list(list_billing_day(day))
    statuses = [billing.status if (billing := billing_of(e)) else None for e in encounters]
    received = sum(
        (
            billing.amount
            for e in encounters
            if (billing := billing_of(e)) and billing.status == BillingStatus.PAGO
        ),
        Decimal("0"),
    )
    return BillingDaySummary(
        paid=statuses.count(BillingStatus.PAGO),
        pending=sum(1 for status in statuses if status in (None, BillingStatus.PENDENTE)),
        released=statuses.count(BillingStatus.LIBERADO),
        received_amount=received,
    )
