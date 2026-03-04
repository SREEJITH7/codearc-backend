import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope.get("user")
        
        if not user or user.is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{str(user.id).replace('-', '')}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "notification",
            "id": event.get("id"),
            "title": event.get("title"),
            "description": event.get("description"),
            "link": event.get("link"),
            "sender_company_name": event.get("sender_company_name"),
            "is_read": event.get("is_read"),
            "created_at": event.get("created_at"),
        }))

