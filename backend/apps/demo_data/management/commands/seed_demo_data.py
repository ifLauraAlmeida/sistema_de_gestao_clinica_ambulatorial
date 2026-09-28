import os
from argparse import ArgumentParser
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.demo_data.fictitious_records import DEMO_USERS
from apps.demo_data.seeding import seed_demo_data

PASSWORD_ENV_VAR = "DEMO_USERS_PASSWORD"
MIN_PASSWORD_LENGTH = 10


class Command(BaseCommand):
    help = "Cria dados FICTÍCIOS de demonstração (somente com DEBUG ativo)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--password",
            help=f"Senha dos usuários de demonstração (ou variável {PASSWORD_ENV_VAR}).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if not settings.DEBUG:
            raise CommandError("Dados de demonstração só podem ser criados com DJANGO_DEBUG=true.")

        password = options["password"] or os.environ.get(PASSWORD_ENV_VAR, "")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise CommandError(
                f"Senha de demonstração inválida: recebido {len(password)} caracteres, "
                f"esperado ao menos {MIN_PASSWORD_LENGTH} (use --password ou {PASSWORD_ENV_VAR})."
            )

        seed_demo_data(password)
        usernames = ", ".join(username for username, *_ in DEMO_USERS)
        self.stdout.write(self.style.SUCCESS(f"Dados fictícios criados. Usuários: {usernames}"))
