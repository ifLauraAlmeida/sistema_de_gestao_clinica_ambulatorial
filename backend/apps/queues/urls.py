from django.urls import path

from apps.queues.views import (
    ReceptionCallView,
    ReceptionForwardView,
    ReceptionQueueView,
    ReceptionRecentCallsView,
)

urlpatterns = [
    path("reception-queue/", ReceptionQueueView.as_view(), name="reception-queue"),
    path(
        "reception-queue/calls/",
        ReceptionRecentCallsView.as_view(),
        name="reception-queue-calls",
    ),
    path(
        "reception-queue/<uuid:entry_id>/call/",
        ReceptionCallView.as_view(),
        name="reception-queue-call",
    ),
    path(
        "reception-queue/<uuid:entry_id>/forward/",
        ReceptionForwardView.as_view(),
        name="reception-queue-forward",
    ),
]
