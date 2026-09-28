from django.apps import AppConfig


class DemoDataConfig(AppConfig):
    """Dados fictícios para desenvolvimento e demonstração (nunca em produção)."""

    name = "apps.demo_data"
    label = "demo_data"
    verbose_name = "Dados de demonstração"
