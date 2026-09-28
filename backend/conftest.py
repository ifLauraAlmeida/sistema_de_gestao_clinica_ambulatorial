"""Fixtures compartilhadas pelos testes do backend. Todos os dados são fictícios."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.accounts.tests.factories import create_user


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def atendente(db) -> User:
    return create_user("ana.recepcao", UserRole.ATENDENTE)


@pytest.fixture
def medico(db) -> User:
    return create_user("bruno.medico", UserRole.MEDICO)


@pytest.fixture
def outro_medico(db) -> User:
    return create_user("carla.medica", UserRole.MEDICO)


@pytest.fixture
def gestor(db) -> User:
    return create_user("diego.gestor", UserRole.GESTOR)


@pytest.fixture
def client_for():
    """Retorna um APIClient autenticado para o usuário informado."""

    def build(user: User) -> APIClient:
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    return build
