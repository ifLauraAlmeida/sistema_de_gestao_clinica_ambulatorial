from typing import Any

from rest_framework import serializers

from apps.accounts.access_permissions import get_user_permissions
from apps.accounts.models import User
from apps.workstations.policies import get_required_station_type
from apps.workstations.selectors import get_open_work_session
from apps.workstations.serializers import WorkSessionSerializer


class LoginSerializer(serializers.Serializer[None]):
    """Credenciais recebidas no login."""

    username = serializers.CharField(max_length=150, trim_whitespace=True)
    password = serializers.CharField(max_length=128, trim_whitespace=False)


class CurrentUserSerializer(serializers.Serializer[User]):
    """
    Contrato do usuário autenticado exposto ao frontend.

    `permissions` serve para montar menus e telas; a autorização real continua
    sendo verificada em cada endpoint.
    """

    id = serializers.UUIDField(read_only=True)
    username = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    role_label = serializers.CharField(source="get_role_display", read_only=True)
    permissions = serializers.SerializerMethodField()
    required_station_type = serializers.SerializerMethodField()
    active_work_session = serializers.SerializerMethodField()

    def get_permissions(self, user: User) -> list[str]:
        return sorted(get_user_permissions(user))

    def get_required_station_type(self, user: User) -> str | None:
        station_type = get_required_station_type(user)
        return str(station_type) if station_type else None

    def get_active_work_session(self, user: User) -> dict[str, Any] | None:
        session = get_open_work_session(user)
        return dict(WorkSessionSerializer(session).data) if session else None
