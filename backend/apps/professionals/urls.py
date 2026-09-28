from django.urls import path

from apps.professionals.views import ProfessionalListView

urlpatterns = [
    path("professionals/", ProfessionalListView.as_view(), name="professionals"),
]
