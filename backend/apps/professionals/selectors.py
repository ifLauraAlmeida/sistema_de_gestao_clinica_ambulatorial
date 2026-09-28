"""Consultas de profissionais."""

import uuid

from apps.accounts.models import User
from apps.professionals.models import Professional


def get_active_professional_for_user(user: User) -> Professional | None:
    """
    Perfil profissional ativo vinculado ao usuário, se existir.

    Exemplo:
        professional = get_active_professional_for_user(medico)
    """
    return (
        Professional.objects.prefetch_related("specialties")
        .filter(user=user, is_active=True)
        .first()
    )


def professional_attends_specialty(professional: Professional, specialty_id: uuid.UUID) -> bool:
    """Indica se a especialidade está entre as do profissional."""
    return professional.specialties.filter(pk=specialty_id, is_active=True).exists()
