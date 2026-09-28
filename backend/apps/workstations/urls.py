from django.urls import path

from apps.workstations.views import (
    AvailableStationsView,
    CurrentWorkSessionView,
    EndCurrentWorkSessionView,
    WorkSessionView,
)

urlpatterns = [
    path("work-sessions/", WorkSessionView.as_view(), name="work-session-start"),
    path("work-sessions/stations/", AvailableStationsView.as_view(), name="work-session-stations"),
    path("work-sessions/current/", CurrentWorkSessionView.as_view(), name="work-session-current"),
    path(
        "work-sessions/current/end/",
        EndCurrentWorkSessionView.as_view(),
        name="work-session-end",
    ),
]
