from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission
from apps.accounts.api_permissions import HasRequiredAccessPermission
from apps.catalog.selectors import (
    active_packages,
    catalog_tree,
    search_laboratory_exams,
    search_services,
)
from apps.catalog.serializers import (
    LaboratoryExamSerializer,
    ServiceCategoryTreeSerializer,
    ServicePackageSerializer,
    ServiceSerializer,
)


class CatalogSearchQuerySerializer(serializers.Serializer[None]):
    search = serializers.CharField(required=False, allow_blank=True, max_length=100)
    category = serializers.UUIDField(required=False)


class CatalogView(APIView):
    """Catálogo completo em árvore: áreas → grupos → serviços."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.CATALOG_VIEW}

    def get(self, request: Request) -> Response:
        return Response(ServiceCategoryTreeSerializer(catalog_tree(), many=True).data)


class ServiceSearchView(APIView):
    """Busca de serviços por nome ou sinônimo (agendamento)."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.CATALOG_VIEW}

    def get(self, request: Request) -> Response:
        query = CatalogSearchQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        services = search_services(
            query.validated_data.get("search", ""), query.validated_data.get("category")
        )
        return Response(ServiceSerializer(services, many=True).data)


class LaboratoryExamListView(APIView):
    """Exames laboratoriais solicitáveis na coleta."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.CATALOG_VIEW}

    def get(self, request: Request) -> Response:
        query = CatalogSearchQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        exams = search_laboratory_exams(query.validated_data.get("search", ""))
        return Response(LaboratoryExamSerializer(exams, many=True).data)


class ServicePackageListView(APIView):
    """Pacotes (check-ups) e seus itens."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.CATALOG_VIEW}

    def get(self, request: Request) -> Response:
        return Response(ServicePackageSerializer(active_packages(), many=True).data)
