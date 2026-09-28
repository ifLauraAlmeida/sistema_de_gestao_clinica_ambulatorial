import uuid

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission
from apps.accounts.api_permissions import HasRequiredAccessPermission
from apps.accounts.request_user import get_authenticated_user
from apps.core.request_metadata import get_client_ip
from apps.encounters.serializers import CheckInSerializer, EncounterSummarySerializer
from apps.encounters.services.check_in import check_in_appointment
from apps.encounters.services.complete_encounter import complete_encounter


class CheckInView(APIView):
    """Confirma a chegada de um paciente agendado."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"POST": AccessPermission.CHECKIN_CREATE}

    def post(self, request: Request) -> Response:
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        encounter = check_in_appointment(
            serializer.validated_data["appointment_id"],
            checked_in_by=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(EncounterSummarySerializer(encounter).data, status=201)


class CompleteEncounterView(APIView):
    """Marca o atendimento como ATENDIDO (médico responsável)."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"POST": AccessPermission.ENCOUNTER_COMPLETE_OWN}

    def post(self, request: Request, encounter_id: uuid.UUID) -> Response:
        encounter = complete_encounter(
            encounter_id,
            completed_by=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(EncounterSummarySerializer(encounter).data)
