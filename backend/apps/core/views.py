from collections.abc import Callable, Sequence
from http import HTTPStatus

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.health_checks import HealthCheck, build_default_health_checks, run_health_checks


class HealthCheckView(APIView):
    """Health check público usado por Docker, proxy e monitoramento."""

    authentication_classes = ()
    permission_classes = (AllowAny,)
    health_checks_factory: Callable[[], Sequence[HealthCheck]] = staticmethod(
        build_default_health_checks
    )

    def get(self, request: Request) -> Response:
        report = run_health_checks(self.health_checks_factory())
        status = HTTPStatus.OK if report.is_healthy else HTTPStatus.SERVICE_UNAVAILABLE
        return Response({"status": report.status, "checks": report.checks}, status=status)
