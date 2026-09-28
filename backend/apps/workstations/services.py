"""Início e encerramento de sessões de trabalho."""

import uuid

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.actions import AuditAction
from apps.audit.services import record_audit_event
from apps.core.exceptions import AccessDeniedError, ResourceNotFoundError
from apps.workstations.models import Station, WorkSession
from apps.workstations.policies import can_occupy_station_type


def start_work_session(
    user: User, station_id: uuid.UUID, *, ip_address: str | None = None
) -> WorkSession:
    """
    Inicia sessão de trabalho no posto, encerrando a sessão anterior do usuário.

    Chamadas feitas na sessão anterior mantêm o destino original, pois cada
    chamada grava um snapshot do posto utilizado.

    Exemplo:
        start_work_session(atendente, station_id=guiche_04.id)
    """
    station = _get_active_station(station_id)
    if not can_occupy_station_type(user, station.station_type):
        _deny_station(user, station, ip_address)

    with transaction.atomic():
        _end_open_session(user, ip_address)
        session = WorkSession.objects.create(
            user=user, station=station, station_type=station.station_type
        )
        record_audit_event(
            action=AuditAction.WORK_SESSION_STARTED,
            user=user,
            entity_type="work_session",
            entity_id=str(session.pk),
            ip_address=ip_address,
            metadata={"station_id": str(station.pk), "station_name": station.name},
        )
    return session


def end_open_work_session(user: User, *, ip_address: str | None = None) -> WorkSession | None:
    """
    Encerra a sessão de trabalho aberta do usuário, se existir.

    Exemplo:
        end_open_work_session(medico)
    """
    with transaction.atomic():
        return _end_open_session(user, ip_address)


def _get_active_station(station_id: uuid.UUID) -> Station:
    station = Station.objects.filter(pk=station_id, is_active=True).first()
    if station is None:
        raise ResourceNotFoundError(
            f"Posto de trabalho não encontrado ou inativo: recebido={station_id}.",
            code="station_not_found",
        )
    return station


def _deny_station(user: User, station: Station, ip_address: str | None) -> None:
    record_audit_event(
        action=AuditAction.ACCESS_DENIED,
        user=user,
        entity_type="station",
        entity_id=str(station.pk),
        ip_address=ip_address,
        metadata={"reason": "station_type_not_allowed", "station_type": station.station_type},
    )
    raise AccessDeniedError(
        f"Seu perfil não pode trabalhar em postos do tipo '{station.get_station_type_display()}'.",
        code="station_type_not_allowed",
    )


def _end_open_session(user: User, ip_address: str | None) -> WorkSession | None:
    session = (
        WorkSession.objects.select_for_update().filter(user=user, ended_at__isnull=True).first()
    )
    if session is None:
        return None
    session.ended_at = timezone.now()
    session.save(update_fields=["ended_at"])
    record_audit_event(
        action=AuditAction.WORK_SESSION_ENDED,
        user=user,
        entity_type="work_session",
        entity_id=str(session.pk),
        ip_address=ip_address,
        metadata={"station_id": str(session.station_id)},
    )
    return session
