from django.http import HttpResponse
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission
from apps.accounts.api_permissions import HasRequiredAccessPermission
from apps.accounts.models import User
from apps.audit.action_catalog import CATEGORY_LABELS
from apps.audit.actions import AuditAction
from apps.audit.csv_export import export_audit_csv
from apps.audit.entity_labels import resolve_entity_labels
from apps.audit.selectors import AuditFilters, search_audit_events, summarize_audit_day
from apps.audit.serializers import AuditEventQuerySerializer, AuditEventSerializer
from apps.audit.services import record_request_audit_event


class AuditEventPagination(PageNumberPagination):
    page_size = 25
    max_page_size = 200
    page_size_query_param = "page_size"


def _filters_from(request: Request) -> AuditFilters:
    query = AuditEventQuerySerializer(data=request.query_params)
    query.is_valid(raise_exception=True)
    params = query.validated_data
    return AuditFilters(
        date_from=params.get("date_from"),
        date_to=params.get("date_to"),
        user_id=params.get("user"),
        category=params.get("category"),
        action=params.get("action"),
        outcome=params.get("outcome"),
        search=params.get("search", ""),
        entity_type=params.get("entity_type"),
        entity_id=params.get("entity_id"),
    )


class AuditEventListView(APIView):
    """Eventos de auditoria filtrados e paginados (somente gestor)."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.AUDIT_VIEW}

    def get(self, request: Request) -> Response:
        events = search_audit_events(_filters_from(request))
        paginator = AuditEventPagination()
        page = paginator.paginate_queryset(events, request, view=self) or []
        serializer = AuditEventSerializer(
            page, many=True, context={"entity_labels": resolve_entity_labels(page)}
        )
        return paginator.get_paginated_response(serializer.data)


class AuditSummaryView(APIView):
    """
    Indicadores do dia e opções de filtro. Abrir a tela de auditoria também é
    auditado, pois ela revela acessos a dados de pacientes.
    """

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.AUDIT_VIEW}

    def get(self, request: Request) -> Response:
        record_request_audit_event(request, action=AuditAction.AUDIT_VIEWED)
        summary = summarize_audit_day(timezone.localdate())
        users = User.objects.order_by("first_name", "username")
        return Response(
            {
                "today": {
                    "total": summary.total,
                    "denied": summary.denied,
                    "medical_records_opened": summary.medical_records_opened,
                    "failed_logins": summary.failed_logins,
                },
                "categories": [
                    {"value": str(category), "label": label}
                    for category, label in CATEGORY_LABELS.items()
                ],
                "users": [
                    {
                        "id": str(user.pk),
                        "display_name": user.display_name,
                        "role_label": user.get_role_display(),
                    }
                    for user in users
                ],
            }
        )


class AuditExportView(APIView):
    """Exporta os eventos filtrados em CSV; a exportação é auditada."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.AUDIT_VIEW}

    def get(self, request: Request) -> HttpResponse:
        filters = _filters_from(request)
        content = export_audit_csv(search_audit_events(filters))
        record_request_audit_event(
            request,
            action=AuditAction.AUDIT_EXPORTED,
            metadata={"rows": content.count("\n") - 1, "search": filters.search or None},
        )
        response = HttpResponse(content, content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="auditoria.csv"'
        return response
