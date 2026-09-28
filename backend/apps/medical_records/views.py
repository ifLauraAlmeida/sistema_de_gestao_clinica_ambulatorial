import uuid

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.request_user import get_authenticated_user
from apps.core.request_metadata import get_client_ip
from apps.encounters.serializers import EncounterSummarySerializer
from apps.medical_records.selectors import list_clinical_history, list_notes_of_encounter
from apps.medical_records.serializers import (
    ClinicalNoteSerializer,
    CreateClinicalNoteSerializer,
    HistoryEncounterSerializer,
    PatientSummarySerializer,
)
from apps.medical_records.services import create_clinical_note, open_medical_record

# Estes endpoints não usam a verificação por perfil: toda decisão (inclusive a
# de perfil) é tomada pela política contextual, que audita concessões e negações
# como MEDICAL_RECORD_VIEW_GRANTED/DENIED.


class MedicalRecordView(APIView):
    """Prontuário do paciente no contexto de um atendimento."""

    def get(self, request: Request, encounter_id: uuid.UUID) -> Response:
        encounter = open_medical_record(
            encounter_id, user=get_authenticated_user(request), ip_address=get_client_ip(request)
        )
        return Response(
            {
                "encounter": EncounterSummarySerializer(encounter).data,
                "patient": PatientSummarySerializer(encounter.patient).data,
                "clinical_notes": ClinicalNoteSerializer(
                    list_notes_of_encounter(encounter), many=True
                ).data,
            }
        )


class ClinicalHistoryView(APIView):
    """Linha do tempo clínica do paciente, acessada via atendimento autorizado."""

    def get(self, request: Request, encounter_id: uuid.UUID) -> Response:
        encounter = open_medical_record(
            encounter_id, user=get_authenticated_user(request), ip_address=get_client_ip(request)
        )
        history = list_clinical_history(encounter)
        return Response(HistoryEncounterSerializer(history, many=True).data)


class ClinicalNoteCollectionView(APIView):
    """Registro de evolução clínica no atendimento ativo."""

    def post(self, request: Request, encounter_id: uuid.UUID) -> Response:
        serializer = CreateClinicalNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = create_clinical_note(
            encounter_id,
            serializer.validated_data["content"],
            author=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(ClinicalNoteSerializer(note).data, status=201)
