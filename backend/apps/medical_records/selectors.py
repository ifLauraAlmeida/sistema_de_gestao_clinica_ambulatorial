"""Consultas de prontuário. Só devem ser usadas após autorização contextual."""

from django.db.models import Prefetch, QuerySet

from apps.encounters.models import Encounter, EncounterStatus
from apps.medical_records.models import ClinicalNote


def list_notes_of_encounter(encounter: Encounter) -> QuerySet[ClinicalNote]:
    """Evoluções do atendimento atual."""
    return encounter.clinical_notes.select_related("author").order_by("created_at")


def list_clinical_history(encounter: Encounter) -> QuerySet[Encounter]:
    """
    Linha do tempo clínica do paciente do atendimento: atendimentos anteriores
    concluídos, do mais recente ao mais antigo, com suas evoluções.
    """
    notes = ClinicalNote.objects.select_related("author").order_by("created_at")
    return (
        Encounter.objects.filter(patient_id=encounter.patient_id, status=EncounterStatus.ATENDIDO)
        .exclude(pk=encounter.pk)
        .select_related("specialty", "professional__user")
        .prefetch_related(Prefetch("clinical_notes", queryset=notes))
        .order_by("-service_date", "-checked_in_at")
    )
