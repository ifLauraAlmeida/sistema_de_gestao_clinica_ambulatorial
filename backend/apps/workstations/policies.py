"""Quais tipos de posto cada perfil pode ocupar."""

from apps.accounts.access_permissions import AccessPermission, user_has_permission
from apps.accounts.models import User
from apps.workstations.models import StationType

_STATION_TYPE_PERMISSIONS: dict[StationType, AccessPermission] = {
    StationType.RECEPTION_DESK: AccessPermission.WORK_SESSION_RECEPTION_DESK,
    StationType.CONSULTATION_ROOM: AccessPermission.WORK_SESSION_CONSULTATION_ROOM,
    StationType.EXAM_ROOM: AccessPermission.WORK_SESSION_EXAM_ROOM,
}


def get_allowed_station_types(user: User) -> list[StationType]:
    """
    Tipos de posto que o usuário pode ocupar.

    Exemplo:
        get_allowed_station_types(atendente)  # [StationType.RECEPTION_DESK]
    """
    return [
        station_type
        for station_type, permission in _STATION_TYPE_PERMISSIONS.items()
        if user_has_permission(user, permission)
    ]


def get_required_station_type(user: User) -> StationType | None:
    """
    Tipo de posto obrigatório antes de operar.

    Perfis com um único tipo permitido (atendente: guichê; médico e
    profissional de saúde: consultório; técnico: sala de exames)
    precisam selecioná-lo após o login. Quem pode ocupar vários tipos (gestor)
    não é obrigado a selecionar posto.
    """
    allowed = get_allowed_station_types(user)
    return allowed[0] if len(allowed) == 1 else None


def can_occupy_station_type(user: User, station_type: str) -> bool:
    """Indica se o usuário pode iniciar sessão em um posto do tipo informado."""
    return station_type in get_allowed_station_types(user)
