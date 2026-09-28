import uuid

from django.conf import settings
from django.db import models


class Specialty(models.Model):
    """
    Especialidade atendida pela clínica.

    `ticket_prefix` forma as senhas da especialidade (ex.: GINE01, ORTO04) e é
    configurável pelo gestor (escopo, seção 15.3).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("nome", max_length=100, unique=True)
    ticket_prefix = models.CharField("prefixo da senha", max_length=6, unique=True)
    is_active = models.BooleanField("ativa", default=True)

    class Meta:
        verbose_name = "especialidade"
        verbose_name_plural = "especialidades"
        ordering = ("name",)
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ticket_prefix__regex=r"^[A-Z]{2,6}$"),
                name="specialty_ticket_prefix_format",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Professional(models.Model):
    """Vínculo entre um usuário e as especialidades em que atende."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="professional_profile"
    )
    specialties = models.ManyToManyField(Specialty, related_name="professionals")
    council_registration = models.CharField(
        "registro no conselho", max_length=32, blank=True, default=""
    )
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "profissional"
        verbose_name_plural = "profissionais"

    def __str__(self) -> str:
        return str(self.user)
