"""Consultas de postos e sessões de trabalho."""

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.workstations.models import Station, StationType, WorkSession
from apps.workstations.policies import get_allowed_station_types


def get_open_work_session(user: User) -> WorkSession | None:
    """
    Sessão de trabalho aberta do usuário, se houver.

    Exemplo:
        session = get_open_work_session(request_user)
    """
    return (
        WorkSession.objects.select_related("station")
        .filter(user=user, ended_at__isnull=True)
        .first()
    )


def get_open_work_session_of_type(user: User, station_type: StationType) -> WorkSession | None:
    """Sessão aberta do usuário somente se o posto for do tipo exigido."""
    session = get_open_work_session(user)
    if session is None or session.station_type != station_type:
        return None
    return session


def list_stations_available_to(user: User) -> QuerySet[Station]:
    """Postos ativos dos tipos que o perfil do usuário pode ocupar."""
    return Station.objects.filter(
        is_active=True, station_type__in=get_allowed_station_types(user)
    ).order_by("station_type", "name")
