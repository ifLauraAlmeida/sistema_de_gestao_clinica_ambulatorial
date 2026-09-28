import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.encounters.models import Encounter
from apps.patients.models import Patient


class ClinicalNote(models.Model):
    """
    Evolução clínica registrada em um atendimento.

    Evoluções não são editadas nem apagadas; correções devem gerar nova
    evolução. `patient` é gravado junto para montar o histórico do paciente.
    Estrutura mínima nesta etapa: o prontuário completo (queixa, conduta,
    diagnóstico, CID...) será modelado no módulo de prontuário.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(
        Encounter, on_delete=models.PROTECT, related_name="clinical_notes"
    )
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="clinical_notes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    content = models.TextField("evolução")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "evolução clínica"
        verbose_name_plural = "evoluções clínicas"
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=("patient", "-created_at"), name="clinical_note_patient_idx"),
        ]

    def __str__(self) -> str:
        return f"Evolução {self.pk}"
