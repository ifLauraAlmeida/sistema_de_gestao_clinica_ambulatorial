from apps.accounts.models import User, UserRole


def create_user(username: str, role: UserRole, *, password: str = "senha-de-teste-123") -> User:
    """Cria usuário fictício para testes."""
    return User.objects.create_user(username=username, password=password, role=role)
