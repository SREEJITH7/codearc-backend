import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope.get("user")
        
        if not user or user.is_anonymous:
            print("Anonymous connection attempt to Notification socket. Closing.")
            await self.close()
            return

        self.group_name = f"user_{user.id}"
        print(f"🔔 Notification socket connecting for user: {user.id}")

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        print(f"✅ Notification socket connected for user: {user.id}")

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            print(f"❌ Notification socket disconnected for user: {self.scope.get('user').id}")

    async def send_notification(self, event):
        # This matches the structure sent from NotificationService.create_and_send
        print(f"📢 Sending real-time notification to user {self.scope.get('user').id}: {event.get('title')}")
        await self.send(text_data=json.dumps({
            "type": "notification",
            "title": event.get("title"),
            "description": event.get("description"),
            "link": event.get("link"),
            "sender_company_name": event.get("sender_company_name"),
        }))

