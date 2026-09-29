from django.urls import path

from apps.catalog.views import (
    CatalogView,
    LaboratoryExamListView,
    ServicePackageListView,
    ServiceSearchView,
)

urlpatterns = [
    path("catalog/", CatalogView.as_view(), name="catalog"),
    path("catalog/services/", ServiceSearchView.as_view(), name="catalog-services"),
    path(
        "catalog/laboratory-exams/",
        LaboratoryExamListView.as_view(),
        name="catalog-laboratory-exams",
    ),
    path("catalog/packages/", ServicePackageListView.as_view(), name="catalog-packages"),
]
