import uuid

from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission
from apps.accounts.api_permissions import HasRequiredAccessPermission
from apps.accounts.request_user import get_authenticated_user
from apps.core.request_metadata import get_client_ip
from apps.patients.models import Patient
from apps.patients.selectors import search_patients
from apps.patients.serializers import PatientDemographicsSerializer, PatientListSerializer
from apps.patients.services import create_patient, update_patient_demographics


class PatientPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = "page_size"


class PatientCollectionView(APIView):
    """Busca e cadastro de pacientes."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {
        "GET": AccessPermission.PATIENT_VIEW_DEMOGRAPHICS,
        "POST": AccessPermission.PATIENT_CREATE,
    }

    def get(self, request: Request) -> Response:
        patients = search_patients(request.query_params.get("search", ""))
        paginator = PatientPagination()
        page = paginator.paginate_queryset(patients, request, view=self)
        return paginator.get_paginated_response(PatientListSerializer(page, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = PatientDemographicsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = create_patient(
            serializer.validated_data,
            created_by=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(PatientDemographicsSerializer(patient).data, status=201)


class PatientDetailView(APIView):
    """Consulta e alteração de dados cadastrais de um paciente."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {
        "GET": AccessPermission.PATIENT_VIEW_DEMOGRAPHICS,
        "PATCH": AccessPermission.PATIENT_UPDATE_DEMOGRAPHICS,
    }

    def get(self, request: Request, patient_id: uuid.UUID) -> Response:
        patient = get_object_or_404(Patient, pk=patient_id)
        return Response(PatientDemographicsSerializer(patient).data)

    def patch(self, request: Request, patient_id: uuid.UUID) -> Response:
        patient = get_object_or_404(Patient, pk=patient_id)
        serializer = PatientDemographicsSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        patient = update_patient_demographics(
            patient,
            serializer.validated_data,
            updated_by=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(PatientDemographicsSerializer(patient).data)
