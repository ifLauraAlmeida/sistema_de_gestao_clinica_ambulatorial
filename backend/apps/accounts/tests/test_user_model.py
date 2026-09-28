import pytest
from django.db import IntegrityError

from apps.accounts.models import User, UserRole


@pytest.mark.django_db
def test_user_has_uuid_primary_key_and_role():
    user = User.objects.create_user(username="atendente.teste", role=UserRole.ATENDENTE)

    assert user.pk is not None
    assert len(str(user.pk)) == 36
    assert user.role == UserRole.ATENDENTE


@pytest.mark.django_db
def test_database_rejects_user_without_valid_role():
    with pytest.raises(IntegrityError):
        User.objects.create_user(username="sem.perfil")


@pytest.mark.django_db
def test_superuser_defaults_to_gestor_role():
    user = User.objects.create_superuser(username="admin.teste", password="x")

    assert user.role == UserRole.GESTOR


def test_display_name_falls_back_to_username():
    assert User(username="medico.teste").display_name == "medico.teste"
    assert User(username="m", first_name="Ana", last_name="Lima").display_name == "Ana Lima"
