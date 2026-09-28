from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.access_permissions import AccessPermission
from apps.accounts.api_permissions import HasRequiredAccessPermission
from apps.professionals.selectors import list_active_professionals
from apps.professionals.serializers import ProfessionalSerializer


class ProfessionalListView(APIView):
    """Profissionais e especialidades disponíveis para agendamento."""

    permission_classes = (HasRequiredAccessPermission,)
    required_permissions = {"GET": AccessPermission.APPOINTMENT_VIEW}

    def get(self, request: Request) -> Response:
        return Response(ProfessionalSerializer(list_active_professionals(), many=True).data)
