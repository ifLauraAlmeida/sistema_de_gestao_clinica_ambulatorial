from django.apps import AppConfig


class EncountersConfig(AppConfig):
    """Atendimentos: check-in, status e vínculo paciente e profissional."""

    name = "apps.encounters"
    label = "encounters"
    verbose_name = "Atendimentos"
