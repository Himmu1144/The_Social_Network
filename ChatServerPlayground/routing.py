from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path
from ChatServerPlayground.asgi import get_asgi_application
django_asgi_app = get_asgi_application()


from public_chat.consumers import PublicChatConsumer

application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter([
				path('public_chat/<room_id>/', PublicChatConsumer.as_asgi()),
    			# re_path(r'ws/public_chat/(?P<room_id>\w+)/$', PublicChatConsumer.as_asgi()),
				]
				
			)
		)
	),
})