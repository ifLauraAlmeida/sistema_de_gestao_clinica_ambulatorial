from django.apps import AppConfig


class ProceduresConfig(AppConfig):
    """Registro da execução de procedimentos e exames (campos por serviço)."""

    name = "apps.procedures"
    label = "procedures"
    verbose_name = "Execução de procedimentos"
