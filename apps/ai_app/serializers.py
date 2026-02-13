from rest_framework import serializers
from .models import AiChatSession, AiChatMessage


class AiChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiChatMessage
        fields = [
            "id",
            "role",
            "content",
            "created_at",
        ]
        read_only_fields = fields


class AiChatSessionSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = AiChatSession
        fields = [
            "id",
            "title",
            "messages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_messages(self, obj):
        # Always return messages in chronological order
        messages = obj.messages.all().order_by("created_at")
        return AiChatMessageSerializer(messages, many=True).data


class AiChatSessionListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = AiChatSession
        fields = [
            "id",
            "title",
            "last_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by("-created_at").first()
        return last_msg.content if last_msg else None
