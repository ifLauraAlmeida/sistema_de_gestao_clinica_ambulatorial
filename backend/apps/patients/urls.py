from django.urls import path

from apps.patients.views import PatientCollectionView, PatientDetailView

urlpatterns = [
    path("patients/", PatientCollectionView.as_view(), name="patients"),
    path("patients/<uuid:patient_id>/", PatientDetailView.as_view(), name="patient-detail"),
]
