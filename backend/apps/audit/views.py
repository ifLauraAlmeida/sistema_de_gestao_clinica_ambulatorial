from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission
from apps.accounts.api_permissions import HasRequiredAccessPermission
from apps.audit.selectors import search_audit_events
from apps.audit.serializers import AuditEventQuerySerializer, AuditEventSerializer


class AuditEventPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 200
    page_size_query_param = "page_size"


class AuditEventListView(APIView):
    """Consulta de auditoria (somente gestor)."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.AUDIT_VIEW}

    def get(self, request: Request) -> Response:
        query = AuditEventQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        events = search_audit_events(**query.validated_data)
        paginator = AuditEventPagination()
        page = paginator.paginate_queryset(events, request, view=self)
        return paginator.get_paginated_response(AuditEventSerializer(page, many=True).data)
