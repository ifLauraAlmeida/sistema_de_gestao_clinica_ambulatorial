from django.urls import path

from apps.audit.views import AuditEventListView, AuditExportView, AuditSummaryView

urlpatterns = [
    path("audit/events/", AuditEventListView.as_view(), name="audit-events"),
    path("audit/summary/", AuditSummaryView.as_view(), name="audit-summary"),
    path("audit/events/export/", AuditExportView.as_view(), name="audit-export"),
]
