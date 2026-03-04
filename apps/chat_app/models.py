import uuid
from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL



class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    application = models.OneToOneField(
        "recruiter_app.Application",
        on_delete=models.CASCADE,
        related_name="conversation"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_conversations"
    )

    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recruiter_conversations"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"
    
class Message(models.Model):
    MESSAGE_TYPES = (
        ("text", "Text"),
        ("file", "File"),
        ("system", "System"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        db_index=True
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default="text")

    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Message {self.id}"
    
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("MESSAGE", "Message"),
        ("SHORTLIST", "Shortlisted"),
        ("OFFER", "Accepted"),
        ("REJECTION", "Rejected"),
        ("TEST", "Test"),
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.CharField(max_length=255, blank=True)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} - {self.recipient}"
