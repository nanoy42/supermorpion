from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import core.routing

application = ProtocolTypeRouter(
    {"websocket": AuthMiddlewareStack(URLRouter(core.routing.websocket_urlpatterns)),}
)
