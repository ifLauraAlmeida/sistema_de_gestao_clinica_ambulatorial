import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.catalog.models import ExecutionFormTemplate
from apps.encounters.models import Encounter


class ProcedureRecord(models.Model):
    """
    Versão dos campos preenchidos na execução do procedimento de um atendimento.

    Somente inserção: cada salvamento cria nova versão, e a mais recente é a
    vigente. Assim nenhum valor é sobrescrito silenciosamente.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(
        Encounter, on_delete=models.PROTECT, related_name="procedure_records"
    )
    template = models.ForeignKey(ExecutionFormTemplate, on_delete=models.PROTECT, related_name="+")
    values = models.JSONField("valores", default=dict)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "registro de procedimento"
        verbose_name_plural = "registros de procedimento"
        ordering = ("-recorded_at",)
        indexes = [
            models.Index(fields=("encounter", "-recorded_at"), name="procedure_record_latest_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.template} — {self.recorded_at:%d/%m/%Y %H:%M}"
