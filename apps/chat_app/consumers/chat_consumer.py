import json
from channels.generic.websocket import AsyncWebsocketConsumer

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from apps.chat_app.models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.conv_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conv_id}"
        user = self.scope["user"]

        # 1️⃣ Reject if unauthenticated
        if user.is_anonymous:
            await self.close()
            return

        # 2️⃣ Validate conversation & participant
        is_valid = await self.validate_conversation(user, self.conv_id)

        if not is_valid:
            await self.close()
            return

        # 3️⃣ Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get("message")
        user = self.scope["user"]

        # Save to DB
        msg_obj = await self.save_message(user, self.conv_id, message_text)

        # Broadcast to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg_obj.content,
                "sender_id": str(user.id),
                "timestamp": str(msg_obj.timestamp),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # ================================
    # DB VALIDATION LOGIC
    # ================================

    @database_sync_to_async
    def validate_conversation(self, user, conv_id):
        try:
            conversation = Conversation.objects.select_related(
                "application__job__recruiter",
                "application__user"
            ).get(id=conv_id, is_active=True)

            # Check if user is candidate
            if conversation.application.user == user:
                return True

            # Check if user is recruiter
            if conversation.application.job.recruiter == user:
                return True

            return False

        except ObjectDoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, user, conv_id, message_text):
        return Message.objects.create(
            conversation_id=conv_id,
            sender=user,
            content=message_text
        )