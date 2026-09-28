from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Infraestrutura compartilhada da API: erros, autenticação, logs e health check."""

    name = "apps.core"
    label = "core"
    verbose_name = "Núcleo"
