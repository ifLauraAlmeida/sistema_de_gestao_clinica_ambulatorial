from django.urls import path

from apps.encounters.views import CheckInView, CompleteEncounterView

urlpatterns = [
    path("check-ins/", CheckInView.as_view(), name="check-ins"),
    path(
        "encounters/<uuid:encounter_id>/complete/",
        CompleteEncounterView.as_view(),
        name="encounter-complete",
    ),
]
