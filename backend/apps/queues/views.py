import uuid

from django.utils import timezone
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission
from apps.accounts.api_permissions import HasRequiredAccessPermission
from apps.accounts.request_user import get_authenticated_user
from apps.core.request_metadata import get_client_ip
from apps.queues.models import QueueType
from apps.queues.selectors import list_active_reception_queue, list_recent_calls
from apps.queues.serializers import QueueCallSerializer, QueueEntrySerializer
from apps.queues.services.call_ticket import call_queue_ticket
from apps.queues.services.forward_to_clinical_queue import forward_to_clinical_queue


class ReceptionQueueView(APIView):
    """Fila ativa da recepção no dia."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.RECEPTION_QUEUE_VIEW}

    def get(self, request: Request) -> Response:
        entries = list_active_reception_queue(timezone.localdate())
        return Response(QueueEntrySerializer(entries, many=True).data)


class ReceptionRecentCallsView(APIView):
    """Últimas chamadas feitas para guichês."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.RECEPTION_QUEUE_VIEW}

    def get(self, request: Request) -> Response:
        calls = list_recent_calls(QueueType.RECEPTION, timezone.localdate())
        return Response(QueueCallSerializer(calls, many=True).data)


class ReceptionCallView(APIView):
    """Chama (ou rechama) a senha para o guichê da sessão de trabalho atual."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"POST": AccessPermission.RECEPTION_QUEUE_CALL}

    def post(self, request: Request, entry_id: uuid.UUID) -> Response:
        call = call_queue_ticket(
            entry_id,
            QueueType.RECEPTION,
            caller=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(QueueCallSerializer(call).data, status=201)


class ReceptionForwardView(APIView):
    """Encaminha o paciente da recepção para a fila do profissional."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"POST": AccessPermission.RECEPTION_QUEUE_FORWARD}

    def post(self, request: Request, entry_id: uuid.UUID) -> Response:
        forward_to_clinical_queue(
            entry_id,
            forwarded_by=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(status=204)
