from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.catalog.models import ServiceAlias, ServicePackage, ServicePackageItem
from apps.catalog.tests.factories import create_laboratory_exam, create_service

pytestmark = pytest.mark.django_db


def test_services_are_found_by_synonym(client_for, atendente):
    service = create_service("Teste ergométrico", category="Cardiologia", group="Ergometria")
    ServiceAlias.objects.create(service=service, name="Ergometria")

    response = client_for(atendente).get("/api/v1/catalog/services/", {"search": "ergometria"})

    assert response.status_code == 200
    [found] = response.json()
    assert found["name"] == "Teste ergométrico"
    assert found["aliases"] == ["Ergometria"]
    assert found["reference_price"] is None


def test_any_catalog_profile_sees_reference_price(client_for, atendente):
    create_service("Raio-X de joelho", reference_price=Decimal("150.00"))

    [found] = client_for(atendente).get("/api/v1/catalog/services/").json()

    assert found["reference_price"] == "150.00"


def test_inactive_services_are_hidden(client_for, atendente):
    create_service("Raio-X de crânio", is_active=False)

    assert client_for(atendente).get("/api/v1/catalog/services/").json() == []


def test_catalog_tree_groups_services_by_area(client_for, atendente):
    create_service("Raio-X de joelho", requires_laterality=True)
    create_service("Raio-X de coluna lombar", group="Coluna")

    [area] = client_for(atendente).get("/api/v1/catalog/").json()

    assert area["name"] == "Raios-X"
    assert sorted(group["name"] for group in area["groups"]) == ["Coluna", "Membro inferior"]


def test_laboratory_exams_have_their_own_table(client_for, atendente):
    create_laboratory_exam("Glicemia de jejum", fasting_hours=8)

    [exam] = client_for(atendente).get("/api/v1/catalog/laboratory-exams/").json()

    assert exam["fasting_hours"] == 8
    assert exam["sample_type_label"] == "Sangue"


def test_package_item_must_be_service_or_exam(db):
    package = ServicePackage.objects.create(name="Pacote preventivo feminino")

    with pytest.raises(IntegrityError):
        ServicePackageItem.objects.create(package=package)


def test_packages_list_items(client_for, atendente):
    package = ServicePackage.objects.create(name="Pacote preventivo masculino")
    ServicePackageItem.objects.create(package=package, laboratory_exam=create_laboratory_exam())

    [found] = client_for(atendente).get("/api/v1/catalog/packages/").json()

    assert found["items"] == [
        {"id": found["items"][0]["id"], "name": "Hemograma completo", "kind": "LABORATORY_EXAM"}
    ]


@pytest.mark.parametrize("user_fixture", ["medico"])
def test_clinical_roles_do_not_browse_catalog(client_for, request, user_fixture):
    user = request.getfixturevalue(user_fixture)

    assert client_for(user).get("/api/v1/catalog/").status_code == 403
