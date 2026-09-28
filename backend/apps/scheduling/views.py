import uuid

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission
from apps.accounts.api_permissions import HasRequiredAccessPermission
from apps.accounts.request_user import get_authenticated_user
from apps.core.request_metadata import get_client_ip
from apps.scheduling.models import Appointment
from apps.scheduling.selectors import AgendaFilters, list_agenda
from apps.scheduling.serializers import (
    AppointmentSerializer,
    CreateAppointmentSerializer,
    UpdateAppointmentSerializer,
)
from apps.scheduling.services import create_appointment, update_appointment


class AgendaQuerySerializer(serializers.Serializer[None]):
    date = serializers.DateField(required=False)
    professional = serializers.UUIDField(required=False)
    specialty = serializers.UUIDField(required=False)
    search = serializers.CharField(required=False, allow_blank=True, max_length=100)


class AppointmentCollectionView(APIView):
    """Agenda do dia e criação de agendamentos."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {
        "GET": AccessPermission.APPOINTMENT_VIEW,
        "POST": AccessPermission.APPOINTMENT_CREATE,
    }

    def get(self, request: Request) -> Response:
        query = AgendaQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        params = query.validated_data
        filters = AgendaFilters(
            day=params.get("date") or timezone.localdate(),
            professional_id=params.get("professional"),
            specialty_id=params.get("specialty"),
            patient_search=params.get("search", ""),
        )
        return Response(AppointmentSerializer(list_agenda(filters), many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CreateAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = create_appointment(
            serializer.validated_data,
            created_by=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(AppointmentSerializer(appointment).data, status=201)


class AppointmentDetailView(APIView):
    """Alteração de horário, status administrativo ou observações."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"PATCH": AccessPermission.APPOINTMENT_UPDATE}

    def patch(self, request: Request, appointment_id: uuid.UUID) -> Response:
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        serializer = UpdateAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = update_appointment(
            appointment,
            serializer.validated_data,
            updated_by=get_authenticated_user(request),
            ip_address=get_client_ip(request),
        )
        return Response(AppointmentSerializer(appointment).data)
