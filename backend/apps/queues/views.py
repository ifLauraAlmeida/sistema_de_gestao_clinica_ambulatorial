import uuid

from django.utils import timezone
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission
from apps.accounts.api_permissions import HasRequiredAccessPermission
from apps.accounts.request_user import get_authenticated_user
from apps.audit.actions import AuditAction
from apps.audit.services import record_request_audit_event
from apps.core.exceptions import AccessDeniedError
from apps.core.request_metadata import get_client_ip
from apps.queues.models import QueueType
from apps.queues.policies import resolve_clinical_queue_owner
from apps.queues.selectors import (
    list_active_reception_queue,
    list_clinical_queue,
    list_recent_calls,
)
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


class ClinicalQueueQuerySerializer(serializers.Serializer[None]):
    status = serializers.ChoiceField(choices=("active", "inactive"), default="active")
    professional_id = serializers.UUIDField(required=False)


class ClinicalQueueView(APIView):
    """
    Fila clínica do dia: ativa (aguardando/chamado) ou inativa (atendidos).

    Médicos veem apenas a própria fila; o gestor pode ver todas ou filtrar.
    """

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {
        "GET": (
            AccessPermission.CLINICAL_QUEUE_VIEW_OWN,
            AccessPermission.CLINICAL_QUEUE_VIEW_INACTIVE_OWN,
            AccessPermission.CLINICAL_QUEUE_VIEW_ALL,
        )
    }

    def get(self, request: Request) -> Response:
        query = ClinicalQueueQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        active = query.validated_data["status"] == "active"
        user = get_authenticated_user(request)
        try:
            owner = resolve_clinical_queue_owner(
                user,
                active=active,
                requested_professional_id=query.validated_data.get("professional_id"),
            )
        except AccessDeniedError:
            record_request_audit_event(
                request,
                action=AuditAction.ACCESS_DENIED,
                entity_type="clinical_queue",
                metadata={"reason": "clinical_queue_out_of_scope"},
            )
            raise
        entries = list_clinical_queue(timezone.localdate(), active=active, professional=owner)
        return Response(QueueEntrySerializer(entries, many=True).data)


class ClinicalCallView(APIView):
    """Chama (ou rechama) a senha para o consultório da sessão de trabalho atual."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {
        "POST": (AccessPermission.CLINICAL_QUEUE_CALL_OWN, AccessPermission.CLINICAL_QUEUE_CALL_ANY)
    }

    def post(self, request: Request, entry_id: uuid.UUID) -> Response:
        call = call_queue_ticket(
            entry_id,
            QueueType.CLINICAL,
            caller=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(QueueCallSerializer(call).data, status=201)
