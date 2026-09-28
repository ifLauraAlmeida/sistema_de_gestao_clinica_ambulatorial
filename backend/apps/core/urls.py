from django.urls import path

from apps.core.views import HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
]
