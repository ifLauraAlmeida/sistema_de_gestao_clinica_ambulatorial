"""Rotas principais. Toda a API é versionada em /api/v1/."""

from django.contrib import admin
from django.urls import include, path

api_v1_patterns = [
    path("", include("apps.core.urls")),
    path("", include("apps.accounts.urls")),
    path("", include("apps.workstations.urls")),
    path("", include("apps.patients.urls")),
    path("", include("apps.professionals.urls")),
    path("", include("apps.scheduling.urls")),
    path("", include("apps.encounters.urls")),
    path("", include("apps.queues.urls")),
    path("", include("apps.medical_records.urls")),
    path("", include("apps.audit.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_patterns)),
]
