import pytest

from apps.catalog.catalog_loader import load_service_catalog
from apps.catalog.models import LaboratoryExam, Service, ServicePackage

pytestmark = pytest.mark.django_db


def test_catalog_load_is_idempotent_and_keeps_manual_prices():
    first = load_service_catalog()
    knee = Service.objects.get(name="Raio-X de joelho")
    knee.reference_price = 120
    knee.save()

    second = load_service_catalog()

    assert first == second
    assert Service.objects.count() == first.services
    knee.refresh_from_db()
    assert knee.reference_price == 120


def test_catalog_encodes_the_clinic_rules():
    load_service_catalog()

    knee = Service.objects.get(name="Raio-X de joelho")
    assert knee.requires_laterality
    assert knee.group.category.name == "Raios-X"
    assert knee.specialty.ticket_prefix == "RX"
    assert knee.form_template.name == "Radiografia"
    assert Service.objects.get(name="Bioimpedância").service_type == "EXAME"
    assert Service.objects.get(name="Sessão de psicologia individual").service_type == "SESSAO"
    assert Service.objects.get(name="Endoscopia digestiva alta").allows_sedation
    ergometry = Service.objects.get(name="Teste ergométrico")
    assert "Ergometria" in {alias.name for alias in ergometry.aliases.all()}
    assert not Service.objects.filter(name__icontains="refluxo").exists()
    assert LaboratoryExam.objects.get(name="Glicemia de jejum").fasting_hours == 8
    feminine = ServicePackage.objects.get(name="Pacote preventivo feminino")
    assert feminine.items.filter(service__name="Mamografia bilateral").exists()
