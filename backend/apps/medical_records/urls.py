from django.urls import path

from apps.medical_records.views import (
    ClinicalHistoryView,
    ClinicalNoteCollectionView,
    MedicalRecordView,
)

urlpatterns = [
    path(
        "encounters/<uuid:encounter_id>/medical-record/",
        MedicalRecordView.as_view(),
        name="medical-record",
    ),
    path(
        "encounters/<uuid:encounter_id>/clinical-history/",
        ClinicalHistoryView.as_view(),
        name="clinical-history",
    ),
    path(
        "encounters/<uuid:encounter_id>/clinical-notes/",
        ClinicalNoteCollectionView.as_view(),
        name="clinical-notes",
    ),
]
