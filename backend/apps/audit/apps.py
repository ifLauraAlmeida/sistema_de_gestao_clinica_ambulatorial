from django.apps import AppConfig


class AuditConfig(AppConfig):
    """Rastreabilidade de operações relevantes e de acessos a dados sensíveis."""

    name = "apps.audit"
    label = "audit"
    verbose_name = "Auditoria"
