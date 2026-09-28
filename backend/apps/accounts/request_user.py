from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request

from apps.accounts.models import User


def get_authenticated_user(request: Request) -> User:
    """
    Retorna o usuário autenticado da requisição.

    Exemplo:
        user = get_authenticated_user(request)
    """
    user = request.user
    if not isinstance(user, User):
        raise NotAuthenticated()
    return user
