from argparse import ArgumentParser
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.demo_data.history import generate_demo_history


class Command(BaseCommand):
    help = "Gera histórico FICTÍCIO dos últimos meses e a agenda futura (somente com DEBUG)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--months", type=int, default=4, help="Meses de histórico (padrão 4).")
        parser.add_argument(
            "--future-days", type=int, default=14, help="Dias de agenda futura (padrão 14)."
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if not settings.DEBUG:
            raise CommandError(
                "Histórico de demonstração só pode ser gerado com DJANGO_DEBUG=true."
            )
        summary = generate_demo_history(options["months"], options["future_days"])
        if summary.skipped:
            self.stdout.write("Histórico já existente: nada foi gerado.")
            return
        self.stdout.write(
            self.style.SUCCESS(
                f"Histórico fictício gerado: {summary.days} dias, {summary.appointments} "
                f"agendamentos, {summary.encounters} atendimentos e "
                f"{summary.future_appointments} agendamentos futuros."
            )
        )
