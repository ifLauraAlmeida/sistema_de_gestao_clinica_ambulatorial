"""Autenticação da API por sessão/cookie do Django."""

from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request


class SessionCookieAuthentication(SessionAuthentication):
    """
    Sessão do Django com CSRF obrigatório para usuários autenticados.

    Informar um esquema em `authenticate_header` faz o DRF responder 401 (e não
    403) para requisições sem sessão, permitindo ao frontend distinguir
    "não autenticado" de "sem permissão".
    """

    def authenticate_header(self, request: Request) -> str:
        return "Session"
