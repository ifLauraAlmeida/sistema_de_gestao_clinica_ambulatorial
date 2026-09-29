import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class StationType(models.TextChoices):
    """Tipos de posto a partir dos quais pacientes podem ser chamados."""

    RECEPTION_DESK = "RECEPTION_DESK", "Guichê de recepção"
    CONSULTATION_ROOM = "CONSULTATION_ROOM", "Consultório"
    EXAM_ROOM = "EXAM_ROOM", "Sala de exames"


class Station(models.Model):
    """
    Posto físico de trabalho, por exemplo "Guichê 04" ou "Consultório 03".

    Postos são desativados em vez de removidos, pois chamadas e sessões
    antigas os referenciam.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    station_type = models.CharField("tipo", max_length=32, choices=StationType.choices)
    name = models.CharField("nome", max_length=64)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "posto de trabalho"
        verbose_name_plural = "postos de trabalho"
        ordering = ("station_type", "name")
        constraints = [
            models.UniqueConstraint(fields=("station_type", "name"), name="station_unique_name"),
            models.CheckConstraint(
                condition=models.Q(station_type__in=StationType.values),
                name="station_type_valid",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class WorkSession(models.Model):
    """
    Período em que um usuário trabalha em um posto.

    O posto não é atributo do usuário: cada login exige nova seleção, e o mesmo
    usuário pode trocar de guichê ou consultório entre turnos. `station_type`
    é gravado como snapshot do tipo do posto no início da sessão.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="work_sessions"
    )
    station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="work_sessions")
    station_type = models.CharField(max_length=32, choices=StationType.choices)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "sessão de trabalho"
        verbose_name_plural = "sessões de trabalho"
        ordering = ("-started_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user",),
                condition=models.Q(ended_at__isnull=True),
                name="work_session_one_open_per_user",
            ),
            models.CheckConstraint(
                condition=models.Q(ended_at__isnull=True)
                | models.Q(ended_at__gte=models.F("started_at")),
                name="work_session_ends_after_start",
            ),
        ]
        indexes = [
            models.Index(fields=("station", "-started_at"), name="work_session_station_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user} @ {self.station}"

    @property
    def is_open(self) -> bool:
        return self.ended_at is None
