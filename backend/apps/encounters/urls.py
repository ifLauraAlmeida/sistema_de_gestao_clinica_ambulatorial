from django.urls import path

from apps.encounters.views import CheckInView

urlpatterns = [
    path("check-ins/", CheckInView.as_view(), name="check-ins"),
]
