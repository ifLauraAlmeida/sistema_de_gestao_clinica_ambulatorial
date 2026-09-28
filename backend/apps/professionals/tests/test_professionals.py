import pytest
from django.db import IntegrityError

from apps.professionals.selectors import (
    get_active_professional_for_user,
    professional_attends_specialty,
)
from apps.professionals.tests.factories import create_professional, create_specialty

pytestmark = pytest.mark.django_db


def test_ticket_prefix_must_be_uppercase_letters():
    with pytest.raises(IntegrityError):
        create_specialty("Ortopedia", "orto1")


def test_active_professional_is_found_for_user(medico):
    gine = create_specialty()
    professional = create_professional(medico, gine)

    assert get_active_professional_for_user(medico) == professional
    assert professional_attends_specialty(professional, gine.id)


def test_inactive_professional_is_ignored(medico):
    professional = create_professional(medico, create_specialty())
    professional.is_active = False
    professional.save()

    assert get_active_professional_for_user(medico) is None


def test_professional_does_not_attend_other_specialty(medico):
    professional = create_professional(medico, create_specialty())
    orto = create_specialty("Ortopedia", "ORTO")

    assert not professional_attends_specialty(professional, orto.id)
