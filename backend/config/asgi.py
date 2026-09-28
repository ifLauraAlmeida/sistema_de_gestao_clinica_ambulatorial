"""
Ponto de entrada ASGI.

HTTP é atendido pelo Django; WebSocket é roteado pelo Channels, com sessão
Django e validação de origem. As rotas WebSocket serão adicionadas junto das
funcionalidades de fila e painel em tempo real.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# A aplicação Django precisa ser carregada antes de importar código que use models.
django_asgi_application = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402

from config.websocket_routes import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_application,
        "websocket": AllowedHostsOriginValidator(
            # types-channels só aceita o tipo privado `_ExtendedURLPattern`, mas a
            # documentação do Channels usa `django.urls.path` para rotas WebSocket.
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))  # type: ignore[arg-type]
        ),
    }
)
