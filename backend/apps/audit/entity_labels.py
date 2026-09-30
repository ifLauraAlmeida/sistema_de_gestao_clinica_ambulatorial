"""
Identificação legível das entidades citadas nos eventos (senha, paciente, serviço).

Resolve em lote, com uma consulta por tipo de entidade, para não gerar N+1 na
listagem. Nunca inclui conteúdo clínico.
"""

from collections import defaultdict
from collections.abc import Iterable

from apps.audit.models import AuditEvent
from apps.encounters.models import Encounter
from apps.patients.models import Patient
from apps.queues.models import QueueEntry
from apps.scheduling.models import Appointment

EntityKey = tuple[str, str]


def resolve_entity_labels(events: Iterable[AuditEvent]) -> dict[EntityKey, str]:
    """
    Mapeia (tipo, id) → descrição curta, por exemplo "RX01 · Raio-X de joelho".

    Exemplo:
        labels = resolve_entity_labels(pagina_de_eventos)
        labels[("encounter", "…")]
    """
    ids_by_type: dict[str, set[str]] = defaultdict(set)
    for event in events:
        if event.entity_id:
            ids_by_type[event.entity_type].add(event.entity_id)
    labels: dict[EntityKey, str] = {}
    for entity_type, resolver in _RESOLVERS.items():
        ids = ids_by_type.get(entity_type)
        if ids:
            labels.update({(entity_type, key): value for key, value in resolver(ids).items()})
    return labels


def _encounter_label(encounter: Encounter) -> str:
    what = encounter.service.name if encounter.service else encounter.specialty.name
    return f"{encounter.ticket_code} · {what} · {encounter.patient.display_name}"


def _encounters(ids: set[str]) -> dict[str, str]:
    encounters = Encounter.objects.filter(pk__in=ids).select_related(
        "service", "specialty", "patient"
    )
    return {str(encounter.pk): _encounter_label(encounter) for encounter in encounters}


def _queue_entries(ids: set[str]) -> dict[str, str]:
    entries = QueueEntry.objects.filter(pk__in=ids).select_related(
        "encounter__service", "encounter__specialty", "encounter__patient"
    )
    return {str(entry.pk): _encounter_label(entry.encounter) for entry in entries}


def _patients(ids: set[str]) -> dict[str, str]:
    return {str(patient.pk): patient.display_name for patient in Patient.objects.filter(pk__in=ids)}


def _appointments(ids: set[str]) -> dict[str, str]:
    appointments = Appointment.objects.filter(pk__in=ids).select_related(
        "patient", "service", "specialty"
    )
    return {
        str(appointment.pk): (
            f"{appointment.patient.display_name} · "
            f"{appointment.service.name if appointment.service else appointment.specialty.name}"
        )
        for appointment in appointments
    }


_RESOLVERS = {
    "encounter": _encounters,
    "queue_entry": _queue_entries,
    "patient": _patients,
    "appointment": _appointments,
}
