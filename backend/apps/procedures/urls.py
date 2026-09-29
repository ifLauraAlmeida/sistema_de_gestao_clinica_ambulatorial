from django.urls import path

from apps.procedures.views import ProcedureView

urlpatterns = [
    path(
        "encounters/<uuid:encounter_id>/procedure/",
        ProcedureView.as_view(),
        name="encounter-procedure",
    ),
]
