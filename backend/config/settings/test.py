"""
Configuração para testes automatizados.

Os testes também utilizam PostgreSQL, para que constraints e comportamentos
transacionais sejam os mesmos de produção.
"""

from .base import *  # noqa: F403
from .base import REST_FRAMEWORK

DEBUG = False

# Hash rápido apenas para acelerar a suíte; nunca usar fora dos testes.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {"login": "1000/min"},
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"handlers": [], "level": "CRITICAL"},
}
