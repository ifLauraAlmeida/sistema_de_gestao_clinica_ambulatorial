"""Consultas de pacientes."""

from django.db.models import Q, QuerySet

from apps.patients.cpf import normalize_cpf
from apps.patients.models import Patient


def search_patients(term: str) -> QuerySet[Patient]:
    """
    Busca pacientes por nome, CPF ou telefone.

    Exemplo:
        search_patients("maria")
        search_patients("529.982.247-25")
    """
    queryset = Patient.objects.all()
    term = term.strip()
    if not term:
        return queryset

    filters = Q(full_name__icontains=term) | Q(social_name__icontains=term)
    digits = normalize_cpf(term)
    if digits:
        filters |= Q(cpf=digits) | Q(phone__contains=digits)
    return queryset.filter(filters)
