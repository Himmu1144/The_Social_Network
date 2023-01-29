from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path
from ChatServerPlayground.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from public_chat.consumers import PublicChatConsumer 
from chat.consumers import ChatConsumer
from notification.consumers import NotificationConsumer

application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter([
				path('', NotificationConsumer.as_asgi()),
				path('chat/<room_id>/', ChatConsumer.as_asgi()),
				path('public_chat/<room_id>/', PublicChatConsumer.as_asgi()),
    			# re_path(r'ws/public_chat/(?P<room_id>\w+)/$', PublicChatConsumer.as_asgi()),
				]
				
			)
		)
	),
})