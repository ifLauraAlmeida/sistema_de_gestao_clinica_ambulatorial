import uuid

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.request_user import get_authenticated_user
from apps.core.request_metadata import get_client_ip
from apps.procedures.serializers import SaveProcedureRecordSerializer, serialize_procedure
from apps.procedures.services import latest_procedure_record, open_procedure, save_procedure_record

# Toda decisão (inclusive de perfil) é tomada pela política do procedimento,
# que audita concessões e negações.


class ProcedureView(APIView):
    """Consulta e preenchimento dos campos do procedimento do atendimento."""

    def get(self, request: Request, encounter_id: uuid.UUID) -> Response:
        encounter, access = open_procedure(
            encounter_id, user=get_authenticated_user(request), ip_address=get_client_ip(request)
        )
        return Response(serialize_procedure(encounter, access, latest_procedure_record(encounter)))

    def put(self, request: Request, encounter_id: uuid.UUID) -> Response:
        serializer = SaveProcedureRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_authenticated_user(request)
        ip_address = get_client_ip(request)
        record = save_procedure_record(
            encounter_id, serializer.validated_data["values"], user=user, ip_address=ip_address
        )
        encounter, access = open_procedure(encounter_id, user=user, ip_address=ip_address)
        return Response(serialize_procedure(encounter, access, record))
