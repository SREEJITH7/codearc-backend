from django.urls import re_path
from .consumers.chat_consumer import ChatConsumer
from .consumers.notification_consumer import NotificationConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<conversation_id>[^/]+)/$", ChatConsumer.as_asgi()),
    re_path(r"^/?ws/notifications/$", NotificationConsumer.as_asgi()),
]