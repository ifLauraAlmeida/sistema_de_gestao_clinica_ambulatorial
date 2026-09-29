from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """Catálogo de serviços: consultas, sessões, procedimentos, exames e pacotes."""

    name = "apps.catalog"
    label = "catalog"
    verbose_name = "Catálogo de serviços"
