from typing import Any

from rest_framework import serializers

from apps.catalog.serializers import ExecutionFormFieldSerializer
from apps.encounters.models import Encounter
from apps.encounters.serializers import EncounterSummarySerializer
from apps.medical_records.serializers import PatientSummarySerializer
from apps.procedures.models import ProcedureRecord
from apps.procedures.policies import ProcedureAccess
from apps.scheduling.service_options import build_preparation_summary


def serialize_procedure(
    encounter: Encounter, access: ProcedureAccess, record: ProcedureRecord | None
) -> dict[str, Any]:
    """
    Contrato da tela de execução: identificação, o que realizar, preparo, campos
    e valores vigentes. Não inclui dados de prontuário.
    """
    service = encounter.service
    template = service.form_template if service else None
    laboratory_exams = (
        list(encounter.appointment.laboratory_exams.all()) if encounter.appointment else []
    )
    return {
        "encounter": EncounterSummarySerializer(encounter).data,
        "patient": PatientSummarySerializer(encounter.patient).data,
        "service_type_label": service.get_service_type_display() if service else None,
        "preparation": build_preparation_summary(service, laboratory_exams),
        "laboratory_exams": [
            {"name": exam.name, "sample_type_label": exam.get_sample_type_display()}
            for exam in laboratory_exams
        ],
        "form": (
            {
                "name": template.name,
                "fields": ExecutionFormFieldSerializer(template.fields.all(), many=True).data,
            }
            if template
            else None
        ),
        "values": record.values if record else None,
        "recorded_at": record.recorded_at if record else None,
        "recorded_by_name": record.recorded_by.display_name if record else None,
        "can_edit": access.can_edit,
    }


class SaveProcedureRecordSerializer(serializers.Serializer[None]):
    # Campos opcionais não preenchidos chegam como null.
    values = serializers.DictField(child=serializers.JSONField(allow_null=True), allow_empty=True)
