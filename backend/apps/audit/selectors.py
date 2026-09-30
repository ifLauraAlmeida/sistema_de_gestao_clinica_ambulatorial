"""Consultas de eventos de auditoria."""

import uuid
from dataclasses import dataclass
from datetime import date

from django.db.models import Q, QuerySet

from apps.audit.action_catalog import DENIAL_ACTIONS, AuditCategory, actions_of_category
from apps.audit.actions import AuditAction
from apps.audit.models import AuditEvent
from apps.encounters.models import Encounter
from apps.patients.models import Patient


@dataclass(frozen=True)
class AuditFilters:
    """Filtros da tela de auditoria."""

    date_from: date | None = None
    date_to: date | None = None
    user_id: uuid.UUID | None = None
    category: AuditCategory | None = None
    action: str | None = None
    outcome: str | None = None  # "denied" | "granted"
    search: str = ""
    entity_type: str | None = None
    entity_id: str | None = None


def search_audit_events(filters: AuditFilters) -> QuerySet[AuditEvent]:
    """
    Eventos filtrados, do mais recente ao mais antigo.

    `search` localiza eventos ligados a um paciente (nome) ou senha (ex.: RX01).

    Exemplo:
        search_audit_events(AuditFilters(outcome="denied", date_from=hoje))
    """
    queryset = AuditEvent.objects.select_related("user").order_by("-timestamp")
    if filters.date_from:
        queryset = queryset.filter(timestamp__date__gte=filters.date_from)
    if filters.date_to:
        queryset = queryset.filter(timestamp__date__lte=filters.date_to)
    if filters.user_id:
        queryset = queryset.filter(user_id=filters.user_id)
    if filters.category:
        queryset = queryset.filter(action__in=actions_of_category(filters.category))
    if filters.action:
        queryset = queryset.filter(action=filters.action)
    if filters.outcome == "denied":
        queryset = queryset.filter(action__in=DENIAL_ACTIONS)
    elif filters.outcome == "granted":
        queryset = queryset.exclude(action__in=DENIAL_ACTIONS)
    if filters.entity_type:
        queryset = queryset.filter(entity_type=filters.entity_type)
    if filters.entity_id:
        queryset = queryset.filter(entity_id=filters.entity_id)
    if filters.search.strip():
        queryset = queryset.filter(_patient_or_ticket_filter(filters.search.strip()))
    return queryset


def _patient_or_ticket_filter(term: str) -> Q:
    patient_ids = [
        str(pk)
        for pk in Patient.objects.filter(
            Q(full_name__icontains=term) | Q(social_name__icontains=term)
        ).values_list("pk", flat=True)
    ]
    encounters = Encounter.objects.filter(
        Q(ticket_code__iexact=term) | Q(patient_id__in=patient_ids)
    )
    encounter_ids = [str(pk) for pk in encounters.values_list("pk", flat=True)]
    queue_entry_ids = [
        str(pk) for pk in encounters.values_list("queue_entries__pk", flat=True) if pk
    ]
    return (
        Q(entity_type="patient", entity_id__in=patient_ids)
        | Q(entity_type="encounter", entity_id__in=encounter_ids)
        | Q(entity_type="queue_entry", entity_id__in=queue_entry_ids)
        | Q(metadata__patient_id__in=patient_ids)
        | Q(metadata__encounter_id__in=encounter_ids)
    )


@dataclass(frozen=True)
class AuditSummary:
    total: int
    denied: int
    medical_records_opened: int
    failed_logins: int


def summarize_audit_day(day: date) -> AuditSummary:
    """Indicadores do dia exibidos no topo da tela de auditoria."""
    events = AuditEvent.objects.filter(timestamp__date=day)
    return AuditSummary(
        total=events.count(),
        denied=events.filter(action__in=DENIAL_ACTIONS).count(),
        medical_records_opened=events.filter(
            action=AuditAction.MEDICAL_RECORD_VIEW_GRANTED
        ).count(),
        failed_logins=events.filter(action=AuditAction.LOGIN_FAILED).count(),
    )
