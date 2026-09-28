"""Formatter de logs estruturados em JSON."""

import json
import logging
from datetime import UTC, datetime


class JsonLogFormatter(logging.Formatter):
    """
    Serializa cada registro de log como uma linha JSON.

    Dados adicionais devem ser enviados em `extra={"context": {...}}` e nunca
    devem conter senhas, tokens, CPF completo ou conteúdo clínico.

    Exemplo:
        logger.info("queue_ticket_called", extra={"context": {"ticket_id": 123}})
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        context = getattr(record, "context", None)
        if isinstance(context, dict):
            payload.update(context)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)
