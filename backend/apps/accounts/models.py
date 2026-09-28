import uuid
from typing import Any, ClassVar

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models


class UserRole(models.TextChoices):
    """Perfis de acesso. Autorizações contextuais complementam o perfil."""

    ATENDENTE = "ATENDENTE", "Atendente"
    MEDICO = "MEDICO", "Médico"
    GESTOR = "GESTOR", "Gestor"


class UserManager(DjangoUserManager["User"]):
    """Manager que garante perfil Gestor para superusuários criados via CLI."""

    def create_superuser(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        extra_fields.setdefault("role", UserRole.GESTOR)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Usuário do sistema. Contas são individuais e intransferíveis.

    Guichê e sala NÃO pertencem ao usuário: são informados a cada sessão de
    trabalho (ver `apps.workstations`).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Sem valor padrão: todo usuário precisa de perfil explícito (negado por padrão).
    role = models.CharField("perfil", max_length=16, choices=UserRole.choices)

    objects: ClassVar[UserManager] = UserManager()

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=UserRole.values),
                name="accounts_user_role_valid",
            ),
        ]

    def __str__(self) -> str:
        return self.username

    @property
    def display_name(self) -> str:
        """Nome exibido na interface; usa o username quando não há nome cadastrado."""
        return self.get_full_name() or self.username
