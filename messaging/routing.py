from django.urls import re_path

from messaging import consumers

websocket_urlpatterns = [
    re_path(
        r"^ws/messages/(?P<conversation_id>[0-9a-f-]{36})/$",
        consumers.ThreadConsumer.as_asgi(),
    ),
]
