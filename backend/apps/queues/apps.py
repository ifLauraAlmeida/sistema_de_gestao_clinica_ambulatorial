from django.apps import AppConfig


class QueuesConfig(AppConfig):
    """Filas de recepção e clínicas, e o registro de cada chamada."""

    name = "apps.queues"
    label = "queues"
    verbose_name = "Filas e chamadas"
