import uuid

from django.conf import settings
from django.db import models


class Patient(models.Model):
    """
    Cadastro único e permanente do paciente.

    O CPF é atributo identificador, nunca chave primária (escopo, seção 38).
    Dados de consultas ficam em atendimentos, não no cadastro.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField("nome completo", max_length=200)
    social_name = models.CharField("nome social", max_length=200, blank=True, default="")
    # NULL (e não "") representa CPF ausente, para que a unicidade valha só para
    # CPFs informados — recomendação da documentação do Django para campos únicos.
    cpf = models.CharField("CPF", max_length=11, null=True, blank=True)  # noqa: DJ001
    birth_date = models.DateField("data de nascimento")
    phone = models.CharField("telefone", max_length=20, blank=True, default="")
    mother_name = models.CharField("nome da mãe", max_length=200, blank=True, default="")
    administrative_notes = models.TextField("observações administrativas", blank=True, default="")
    is_active = models.BooleanField("ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        verbose_name = "paciente"
        verbose_name_plural = "pacientes"
        ordering = ("full_name",)
        constraints = [
            models.UniqueConstraint(
                fields=("cpf",), condition=models.Q(cpf__isnull=False), name="patient_unique_cpf"
            ),
            models.CheckConstraint(
                condition=models.Q(cpf__isnull=True) | models.Q(cpf__regex=r"^\d{11}$"),
                name="patient_cpf_digits_only",
            ),
        ]
        indexes = [
            models.Index(fields=("full_name",), name="patient_full_name_idx"),
            models.Index(fields=("birth_date",), name="patient_birth_date_idx"),
        ]

    def __str__(self) -> str:
        return self.display_name

    @property
    def display_name(self) -> str:
        """Nome social tem prioridade sobre o nome civil na exibição."""
        return self.social_name or self.full_name
