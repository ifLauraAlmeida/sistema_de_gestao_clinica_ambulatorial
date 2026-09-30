import uuid

from django.conf import settings
from django.db import models

from apps.encounters.models import Encounter


class HealthInsurer(models.Model):
    """Convênio / operadora aceita pela clínica."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("nome", max_length=120, unique=True)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "convênio"
        verbose_name_plural = "convênios"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class PayerType(models.TextChoices):
    PARTICULAR = "PARTICULAR", "Particular"
    CONVENIO = "CONVENIO", "Convênio"


class BillingStatus(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    PAGO = "PAGO", "Pago"
    LIBERADO = "LIBERADO", "Liberado"


class PaymentMethod(models.TextChoices):
    DINHEIRO = "DINHEIRO", "Dinheiro"
    PIX = "PIX", "Pix"
    CARTAO_DEBITO = "CARTAO_DEBITO", "Cartão de débito"
    CARTAO_CREDITO = "CARTAO_CREDITO", "Cartão de crédito"


class EncounterBilling(models.Model):
    """
    Situação financeira de um atendimento: pagamento particular ou autorização
    (guia) do convênio. Mudanças ficam na auditoria com situação anterior e nova.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.OneToOneField(Encounter, on_delete=models.PROTECT, related_name="billing")
    payer_type = models.CharField("pagador", max_length=16, choices=PayerType.choices)
    insurer = models.ForeignKey(
        HealthInsurer, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    guide_number = models.CharField("número da guia", max_length=40, blank=True, default="")
    payment_method = models.CharField(
        "forma de pagamento", max_length=16, choices=PaymentMethod.choices, blank=True, default=""
    )
    amount = models.DecimalField("valor", max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=16, choices=BillingStatus.choices, default=BillingStatus.PENDENTE
    )
    settled_at = models.DateTimeField("pago/liberado em", null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "financeiro do atendimento"
        verbose_name_plural = "financeiro dos atendimentos"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0), name="billing_amount_not_negative"
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(payer_type=PayerType.PARTICULAR, insurer__isnull=True)
                    | models.Q(payer_type=PayerType.CONVENIO, insurer__isnull=False)
                ),
                name="billing_insurer_matches_payer",
            ),
            models.CheckConstraint(
                condition=~models.Q(status=BillingStatus.PAGO) | ~models.Q(payment_method=""),
                name="billing_paid_has_method",
            ),
            models.CheckConstraint(
                condition=~models.Q(status=BillingStatus.LIBERADO)
                | (models.Q(payer_type=PayerType.CONVENIO) & ~models.Q(guide_number="")),
                name="billing_released_has_guide",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=BillingStatus.values), name="billing_status_valid"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.encounter} — {self.get_status_display()}"
