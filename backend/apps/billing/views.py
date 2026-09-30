import uuid
from datetime import timedelta

from django.utils import timezone
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission
from apps.accounts.api_permissions import HasRequiredAccessPermission
from apps.accounts.request_user import get_authenticated_user
from apps.billing.models import HealthInsurer
from apps.billing.selectors import list_billing_day, summarize_billing_day
from apps.billing.serializers import (
    AuthorizationSerializer,
    BillingDayQuerySerializer,
    HealthInsurerSerializer,
    PaymentSerializer,
    serialize_billing_entry,
    serialize_summary,
)
from apps.billing.services import confirm_payment, release_authorization
from apps.core.request_metadata import get_client_ip


class BillingDayView(APIView):
    """Pacientes do dia com situação financeira e indicadores comparados ao dia anterior."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.BILLING_VIEW_HISTORY}

    def get(self, request: Request) -> Response:
        query = BillingDayQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        day = query.validated_data.get("date") or timezone.localdate()
        return Response(
            {
                "date": day,
                "today": serialize_summary(summarize_billing_day(day)),
                "previous_day": serialize_summary(summarize_billing_day(day - timedelta(days=1))),
                "entries": [serialize_billing_entry(e) for e in list_billing_day(day)],
            }
        )


class HealthInsurerListView(APIView):
    """Convênios ativos."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.BILLING_VIEW_HISTORY}

    def get(self, request: Request) -> Response:
        insurers = HealthInsurer.objects.filter(is_active=True).order_by("name")
        return Response(HealthInsurerSerializer(insurers, many=True).data)


class PaymentView(APIView):
    """Confirma o pagamento do atendimento."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"POST": AccessPermission.BILLING_MANAGE}

    def post(self, request: Request, encounter_id: uuid.UUID) -> Response:
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        billing = confirm_payment(
            encounter_id,
            **serializer.validated_data,
            confirmed_by=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(serialize_billing_entry(billing.encounter))


class AuthorizationView(APIView):
    """Libera o atendimento pela guia autorizada do convênio."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"POST": AccessPermission.BILLING_MANAGE}

    def post(self, request: Request, encounter_id: uuid.UUID) -> Response:
        serializer = AuthorizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        billing = release_authorization(
            encounter_id,
            **serializer.validated_data,
            released_by=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(serialize_billing_entry(billing.encounter))
