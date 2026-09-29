"""Consultas do catálogo (somente itens ativos)."""

import uuid

from django.db.models import Prefetch, Q, QuerySet

from apps.catalog.models import (
    LaboratoryExam,
    Service,
    ServiceCategory,
    ServiceGroup,
    ServicePackage,
    ServicePackageItem,
)


def active_services() -> QuerySet[Service]:
    """Serviços ativos com área, grupo, especialidade e sinônimos carregados."""
    return (
        Service.objects.filter(
            is_active=True, group__is_active=True, group__category__is_active=True
        )
        .select_related("group__category", "specialty")
        .prefetch_related("aliases")
    )


def search_services(term: str = "", category_id: uuid.UUID | None = None) -> QuerySet[Service]:
    """
    Busca serviços por nome ou sinônimo, opcionalmente dentro de uma área.

    Exemplo:
        search_services("ergometria")  # encontra "Teste ergométrico"
    """
    queryset = active_services()
    if category_id:
        queryset = queryset.filter(group__category_id=category_id)
    term = term.strip()
    if term:
        queryset = queryset.filter(Q(name__icontains=term) | Q(aliases__name__icontains=term))
    return queryset.distinct().order_by(
        "group__category__display_order", "group__display_order", "display_order", "name"
    )


def catalog_tree() -> QuerySet[ServiceCategory]:
    """Áreas → grupos → serviços ativos, em três consultas."""
    services = active_services().order_by("display_order", "name")
    groups = (
        ServiceGroup.objects.filter(is_active=True)
        .order_by("display_order", "name")
        .prefetch_related(Prefetch("services", queryset=services))
    )
    return (
        ServiceCategory.objects.filter(is_active=True)
        .order_by("display_order", "name")
        .prefetch_related(Prefetch("groups", queryset=groups))
    )


def search_laboratory_exams(term: str = "") -> QuerySet[LaboratoryExam]:
    """Exames laboratoriais ativos, filtrados por nome ou grupo."""
    queryset = LaboratoryExam.objects.filter(is_active=True)
    if term.strip():
        queryset = queryset.filter(Q(name__icontains=term) | Q(group__icontains=term))
    return queryset.order_by("group", "name")


def active_packages() -> QuerySet[ServicePackage]:
    """Pacotes ativos com seus itens."""
    items = ServicePackageItem.objects.select_related("service", "laboratory_exam")
    return (
        ServicePackage.objects.filter(is_active=True)
        .prefetch_related(Prefetch("items", queryset=items))
        .order_by("name")
    )
