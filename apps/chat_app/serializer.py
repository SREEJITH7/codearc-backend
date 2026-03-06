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
    company_name = serializers.CharField(source="recruiter.recruiter_profile.company_name", read_only=True)
    applicant_name = serializers.CharField(source="application.name", read_only=True)
    application_id = serializers.UUIDField(source="application.id", read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id", "user", "recruiter", "company_name", "applicant_name", "application_id",
            "last_message", "unread_count", "created_at"
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by("-timestamp").first()
        if last_msg:
            return {
                "content": last_msg.content,
                "timestamp": last_msg.timestamp,
                "sender_id": last_msg.sender_id
            }
        return None

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()


class NotificationSerializer(serializers.ModelSerializer):
    sender_company_name = serializers.CharField(source="sender.recruiter_profile.company_name", read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
