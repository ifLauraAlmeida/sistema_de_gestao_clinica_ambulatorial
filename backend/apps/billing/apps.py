from django.apps import AppConfig


class BillingConfig(AppConfig):
    """Pagamentos particulares e autorizações de convênio dos atendimentos."""

    name = "apps.billing"
    label = "billing"
    verbose_name = "Financeiro e autorizações"
