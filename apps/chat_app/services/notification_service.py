from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.chat_app.models import Notification


class NotificationService:

    @staticmethod
    def create_and_send(recipient, sender, notif_type, title, description, link=""):
        # Save to DB
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            type=notif_type,
            title=title,
            description=description,
            link=link
        )
        # Send real-time event
        channel_layer = get_channel_layer()

        company_name = getattr(sender.recruiter_profile, 'company_name', None) if sender and hasattr(sender, 'recruiter_profile') else None

        group_name = f"user_{str(recipient.id).replace('-', '')}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "id": notification.id,
                "title": title,
                "description": description,
                "link": link,
                "sender_company_name": company_name,
                "is_read": False,
                "created_at": notification.created_at.isoformat(),
            }
        )


        return notification