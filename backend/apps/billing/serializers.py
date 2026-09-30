from typing import Any

from rest_framework import serializers

from apps.billing.models import HealthInsurer, PaymentMethod
from apps.billing.selectors import BillingDaySummary, billing_of, expected_amount
from apps.encounters.models import Encounter


def serialize_billing_entry(encounter: Encounter) -> dict[str, Any]:
    """Linha de "Pacientes de hoje" (Tela 09)."""
    billing = billing_of(encounter)
    amount = expected_amount(encounter)
    return {
        "encounter_id": str(encounter.pk),
        "ticket_code": encounter.ticket_code,
        "patient_name": encounter.patient.display_name,
        "service_name": encounter.service.name if encounter.service else encounter.specialty.name,
        "payer_label": (
            billing.insurer.name
            if billing and billing.insurer
            else "Particular"
            if billing
            else "—"
        ),
        "insurer_id": str(billing.insurer_id) if billing and billing.insurer_id else None,
        "guide_number": billing.guide_number if billing else "",
        "payment_method": billing.payment_method if billing else "",
        "status": billing.status if billing else "PENDENTE",
        "status_label": billing.get_status_display() if billing else "Pendente",
        "amount": str(amount) if amount is not None else None,
    }


def serialize_summary(summary: BillingDaySummary) -> dict[str, Any]:
    return {
        "paid": summary.paid,
        "pending": summary.pending,
        "released": summary.released,
        "received_amount": str(summary.received_amount),
    }


class HealthInsurerSerializer(serializers.ModelSerializer[HealthInsurer]):
    class Meta:
        model = HealthInsurer
        fields = ("id", "name")
        read_only_fields = fields


class PaymentSerializer(serializers.Serializer[None]):
    """Pagamento particular ou coparticipação (com convênio)."""

    insurer = serializers.PrimaryKeyRelatedField(
        queryset=HealthInsurer.objects.filter(is_active=True),
        required=False,
        allow_null=True,
        default=None,
    )
    guide_number = serializers.CharField(
        required=False, allow_blank=True, max_length=40, default=""
    )
    payment_method = serializers.ChoiceField(choices=PaymentMethod.choices)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)


class AuthorizationSerializer(serializers.Serializer[None]):
    """Liberação pela guia autorizada do convênio."""

    insurer = serializers.PrimaryKeyRelatedField(
        queryset=HealthInsurer.objects.filter(is_active=True)
    )
    guide_number = serializers.CharField(max_length=40)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)


class BillingDayQuerySerializer(serializers.Serializer[None]):
    date = serializers.DateField(required=False)
