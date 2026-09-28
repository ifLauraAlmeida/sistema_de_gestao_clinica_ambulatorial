from django.urls import path

from apps.encounters.views import CheckInView, CompleteEncounterView, StartEncounterView

urlpatterns = [
    path("check-ins/", CheckInView.as_view(), name="check-ins"),
    path(
        "encounters/<uuid:encounter_id>/start/",
        StartEncounterView.as_view(),
        name="encounter-start",
    ),
    path(
        "encounters/<uuid:encounter_id>/complete/",
        CompleteEncounterView.as_view(),
        name="encounter-complete",
    ),
]
