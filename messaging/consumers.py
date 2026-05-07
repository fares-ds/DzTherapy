"""WebSocket consumer for real-time message delivery.

Each Conversation has a channel-layer group `chat-<uuid>`. When the HTTP
`send_message` view persists a message it broadcasts a render hint to that
group; every connected participant's browser receives `{"type": "new"}` and
re-fetches the partial via HTMX (sse-style server-driven swap).

Falls back gracefully when no Redis is available — `InMemoryChannelLayer`
works in dev/CI but is per-process so multi-worker deploys MUST configure
`REDIS_URL`.
"""

from __future__ import annotations

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from messaging.models import Conversation


class ThreadConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        allowed = await self._user_in_conversation(user, conversation_id)
        if not allowed:
            await self.close(code=4403)
            return

        self.group_name = f"chat-{conversation_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_new(self, event):
        """Group-message handler: broadcast to the participant's browser."""
        await self.send_json({"type": "new", "message_id": event.get("message_id")})

    @database_sync_to_async
    def _user_in_conversation(self, user, conversation_id) -> bool:
        try:
            convo = Conversation.objects.select_related("therapist").get(
                id=conversation_id
            )
        except Conversation.DoesNotExist:
            return False
        return convo.includes(user)
