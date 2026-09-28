"""Consultas de profissionais."""

import uuid

from django.db.models import Prefetch, QuerySet

from apps.accounts.models import User
from apps.professionals.models import Professional, Specialty


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


def list_active_professionals() -> QuerySet[Professional]:
    """Profissionais ativos com especialidades ativas, para agenda e filtros."""
    active_specialties = Specialty.objects.filter(is_active=True).order_by("name")
    return (
        Professional.objects.filter(is_active=True, user__is_active=True)
        .select_related("user")
        .prefetch_related(Prefetch("specialties", queryset=active_specialties))
        .order_by("user__first_name", "user__last_name")
    )
