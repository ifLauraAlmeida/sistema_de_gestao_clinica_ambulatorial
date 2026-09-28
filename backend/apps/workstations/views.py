from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.request_user import get_authenticated_user
from apps.core.request_metadata import get_client_ip
from apps.workstations.selectors import get_open_work_session, list_stations_available_to
from apps.workstations.serializers import (
    StartWorkSessionSerializer,
    StationSerializer,
    WorkSessionSerializer,
)
from apps.workstations.services import end_open_work_session, start_work_session


class AvailableStationsView(APIView):
    """Lista guichês/consultórios que o perfil do usuário pode ocupar."""

    def get(self, request: Request) -> Response:
        stations = list_stations_available_to(get_authenticated_user(request))
        return Response(StationSerializer(stations, many=True).data)


class WorkSessionView(APIView):
    """Inicia uma sessão de trabalho em um posto."""

    def post(self, request: Request) -> Response:
        serializer = StartWorkSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = start_work_session(
            get_authenticated_user(request),
            serializer.validated_data["station_id"],
            ip_address=get_client_ip(request),
        )
        return Response(WorkSessionSerializer(session).data, status=201)


class CurrentWorkSessionView(APIView):
    """Consulta a sessão de trabalho aberta do usuário."""

    def get(self, request: Request) -> Response:
        session = get_open_work_session(get_authenticated_user(request))
        data = WorkSessionSerializer(session).data if session else None
        return Response({"work_session": data})


class EndCurrentWorkSessionView(APIView):
    """Encerra a sessão de trabalho aberta do usuário."""

    def post(self, request: Request) -> Response:
        end_open_work_session(get_authenticated_user(request), ip_address=get_client_ip(request))
        return Response(status=204)
