from typing import Any

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.request_user import get_authenticated_user
from apps.accounts.serializers import CurrentUserSerializer, LoginSerializer
from apps.accounts.services.session_login import login_user, logout_user


def serialize_current_user(user: User) -> dict[str, Any]:
    """Serializa o usuário autenticado no contrato usado pelo frontend."""
    return dict(CurrentUserSerializer(user).data)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfCookieView(APIView):
    """Entrega o cookie CSRF necessário para o login e demais requisições de escrita."""

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        return Response(status=204)


# Login ocorre antes de existir sessão autenticada, então o DRF não validaria o
# CSRF por conta própria; `csrf_protect` torna a validação obrigatória.
@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    """Autentica usuário e senha e cria a sessão."""

    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "login"

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = login_user(
            request._request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        return Response(serialize_current_user(user))


class LogoutView(APIView):
    """Encerra a sessão do usuário autenticado."""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        logout_user(request._request)
        return Response(status=204)


class CurrentUserView(APIView):
    """Retorna o usuário autenticado, seu perfil e permissões."""

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        return Response(serialize_current_user(get_authenticated_user(request)))
