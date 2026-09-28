"""Metadados de requisição usados em auditoria."""

from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> str | None:
    """
    Retorna o IP do cliente conforme recebido pelo servidor.

    Cabeçalhos como X-Forwarded-For não são considerados porque podem ser
    forjados pelo cliente; quando houver proxy reverso confiável, ele deve
    repassar o IP real de forma explícita.
    """
    remote_address = request.META.get("REMOTE_ADDR")
    return remote_address or None
