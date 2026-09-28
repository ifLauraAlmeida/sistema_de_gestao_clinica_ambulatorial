"""Consultas da agenda."""

from datetime import date

from django.db.models import QuerySet

from apps.scheduling.models import Appointment


def list_appointments_for_day(day: date) -> QuerySet[Appointment]:
    """
    Agendamentos do dia, com paciente, profissional e especialidade carregados.

    Exemplo:
        list_appointments_for_day(date(2026, 9, 28))
    """
    return (
        Appointment.objects.select_related("patient", "professional__user", "specialty")
        .filter(scheduled_for__date=day)
        .order_by("scheduled_for")
    )
