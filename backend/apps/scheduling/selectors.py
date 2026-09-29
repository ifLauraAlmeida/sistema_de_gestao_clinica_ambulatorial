"""Consultas da agenda."""

import uuid
from dataclasses import dataclass
from datetime import date

from django.db.models import Q, QuerySet

from apps.patients.cpf import normalize_cpf
from apps.scheduling.models import Appointment


@dataclass(frozen=True)
class AgendaFilters:
    """Filtros da agenda do dia (Tela 04 e check-in)."""

    day: date
    professional_id: uuid.UUID | None = None
    specialty_id: uuid.UUID | None = None
    patient_search: str = ""


def list_agenda(filters: AgendaFilters) -> QuerySet[Appointment]:
    """
    Agendamentos do dia filtrados, com paciente, profissional, especialidade e
    senha (quando já houve check-in) carregados em uma única consulta.

    Exemplo:
        list_agenda(AgendaFilters(day=date(2026, 9, 28), patient_search="maria"))
    """
    queryset = (
        Appointment.objects.select_related(
            "patient", "professional__user", "specialty", "encounter", "service"
        )
        .prefetch_related("laboratory_exams")
        .filter(scheduled_for__date=filters.day)
    )
    if filters.professional_id:
        queryset = queryset.filter(professional_id=filters.professional_id)
    if filters.specialty_id:
        queryset = queryset.filter(specialty_id=filters.specialty_id)
    if filters.patient_search.strip():
        queryset = queryset.filter(_patient_search_filter(filters.patient_search.strip()))
    return queryset.order_by("scheduled_for")


def _patient_search_filter(term: str) -> Q:
    condition = Q(patient__full_name__icontains=term) | Q(patient__social_name__icontains=term)
    digits = normalize_cpf(term)
    if digits:
        condition |= Q(patient__cpf=digits) | Q(patient__phone__contains=digits)
    return condition
