from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Usuários, perfis, autenticação e permissões."""

    name = "apps.accounts"
    label = "accounts"
    verbose_name = "Contas de usuário"
