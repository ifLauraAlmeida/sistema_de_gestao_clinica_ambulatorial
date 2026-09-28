FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Ferramentas de desenvolvimento (pytest, ruff, mypy) só entram na imagem de dev.
ARG INSTALL_DEV_DEPENDENCIES=false
ARG APP_UID=1000

WORKDIR /app

RUN useradd --create-home --uid "${APP_UID}" appuser

COPY pyproject.toml ./
RUN if [ "$INSTALL_DEV_DEPENDENCIES" = "true" ]; then pip install ".[dev]"; else pip install .; fi \
    && rm -rf build *.egg-info

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

CMD ["daphne", "--bind", "0.0.0.0", "--port", "8000", "config.asgi:application"]
