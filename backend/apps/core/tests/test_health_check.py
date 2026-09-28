import pytest
from rest_framework.test import APIClient, APIRequestFactory

from apps.core.health_checks import run_health_checks
from apps.core.tests.fakes import FakeHealthCheck
from apps.core.views import HealthCheckView


def _call_health_view(*checks: FakeHealthCheck):
    view = HealthCheckView.as_view(health_checks_factory=lambda: list(checks))
    return view(APIRequestFactory().get("/api/v1/health/"))


def test_report_is_ok_when_every_dependency_is_healthy():
    report = run_health_checks([FakeHealthCheck("database", True), FakeHealthCheck("redis", True)])

    assert report.status == "ok"
    assert report.checks == {"database": "ok", "redis": "ok"}


def test_report_is_unavailable_when_any_dependency_fails():
    report = run_health_checks([FakeHealthCheck("database", True), FakeHealthCheck("redis", False)])

    assert report.status == "unavailable"
    assert report.checks["redis"] == "unavailable"


def test_health_view_returns_200_when_healthy():
    response = _call_health_view(FakeHealthCheck("database", True))

    assert response.status_code == 200
    assert response.data == {"status": "ok", "checks": {"database": "ok"}}


def test_health_view_returns_503_without_exposing_details_when_unhealthy():
    response = _call_health_view(FakeHealthCheck("database", False))

    assert response.status_code == 503
    assert response.data == {"status": "unavailable", "checks": {"database": "unavailable"}}


@pytest.mark.django_db
def test_health_endpoint_is_public_and_checks_real_database():
    response = APIClient().get("/api/v1/health/")

    assert response.status_code in (200, 503)
    assert response.json()["checks"]["database"] == "ok"
