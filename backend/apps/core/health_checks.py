"""
Verificações de saúde das dependências de infraestrutura.

O resultado indica apenas "ok"/"unavailable" por dependência, sem expor
versões, hosts ou mensagens de erro.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

import redis
from django.conf import settings
from django.db import DatabaseError, connection

HEALTHY = "ok"
UNAVAILABLE = "unavailable"


class HealthCheck(Protocol):
    """Dependência verificável pelo health check."""

    name: str

    def is_healthy(self) -> bool: ...


@dataclass(frozen=True)
class HealthReport:
    """Resultado consolidado das verificações."""

    status: str
    checks: dict[str, str]

    @property
    def is_healthy(self) -> bool:
        return self.status == HEALTHY


class DatabaseHealthCheck:
    """Confirma que o PostgreSQL responde a uma consulta simples."""

    name = "database"

    def is_healthy(self) -> bool:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except DatabaseError:
            return False
        return True


class RedisHealthCheck:
    """Confirma que o Redis (camada de eventos em tempo real) responde a PING."""

    name = "redis"

    def __init__(self, redis_url: str, timeout_seconds: float = 1.0) -> None:
        self._redis_url = redis_url
        self._timeout_seconds = timeout_seconds

    def is_healthy(self) -> bool:
        client = redis.Redis.from_url(
            self._redis_url,
            socket_connect_timeout=self._timeout_seconds,
            socket_timeout=self._timeout_seconds,
        )
        try:
            return bool(client.ping())
        except redis.RedisError:
            return False
        finally:
            client.close()


def build_default_health_checks() -> list[HealthCheck]:
    """Retorna as verificações padrão da aplicação (PostgreSQL e Redis)."""
    return [DatabaseHealthCheck(), RedisHealthCheck(settings.REDIS_URL)]


def run_health_checks(checks: Sequence[HealthCheck]) -> HealthReport:
    """
    Executa as verificações e consolida o resultado.

    Exemplo:
        report = run_health_checks(build_default_health_checks())
        report.status  # "ok" ou "unavailable"
    """
    results = {check.name: HEALTHY if check.is_healthy() else UNAVAILABLE for check in checks}
    overall = HEALTHY if all(value == HEALTHY for value in results.values()) else UNAVAILABLE
    return HealthReport(status=overall, checks=results)
