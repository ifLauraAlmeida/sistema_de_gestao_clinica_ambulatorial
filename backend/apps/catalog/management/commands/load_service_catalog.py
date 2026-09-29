from typing import Any

from django.core.management.base import BaseCommand

from apps.catalog.catalog_loader import load_service_catalog


class Command(BaseCommand):
    help = "Carrega (ou atualiza) o catálogo inicial de serviços, exames e pacotes."

    def handle(self, *args: Any, **options: Any) -> None:
        summary = load_service_catalog()
        self.stdout.write(
            self.style.SUCCESS(
                f"Catálogo carregado: {summary.services} serviços, "
                f"{summary.laboratory_exams} exames laboratoriais, "
                f"{summary.packages} pacotes, {summary.specialties} especialidades."
            )
        )
