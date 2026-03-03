from rest_framework import serializers
from .models import Conversation, Message, Notification


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_username",
            "content",
            "message_type",
            "is_read",
            "timestamp",
        ]
        read_only_fields = ["id", "sender", "timestamp"]


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    sender_company_name = serializers.CharField(source="sender.recruiter_profile.company_name", read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
