from django.urls import path

from apps.scheduling.views import AppointmentCollectionView, AppointmentDetailView

urlpatterns = [
    path("appointments/", AppointmentCollectionView.as_view(), name="appointments"),
    path(
        "appointments/<uuid:appointment_id>/",
        AppointmentDetailView.as_view(),
        name="appointment-detail",
    ),
]
