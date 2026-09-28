"""Configuração para desenvolvimento local."""

from .base import *  # noqa: F403
from .base import env

DEBUG = env.bool("DJANGO_DEBUG", default=True)

# Em desenvolvimento o Vite encaminha /api para o backend (mesma origem para o
# navegador). A origem do Vite precisa ser confiável para a validação de CSRF.
CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=["http://localhost:5173", "http://127.0.0.1:5173"],
)
