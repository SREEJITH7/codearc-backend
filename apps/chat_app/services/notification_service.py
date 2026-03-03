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
        print(f"Sending notification to group user_{recipient.id}")
        # Send real-time event
        channel_layer = get_channel_layer()

        company_name = getattr(sender.recruiter_profile, 'company_name', None) if sender and hasattr(sender, 'recruiter_profile') else None

        async_to_sync(channel_layer.group_send)(
            f"user_{recipient.id}",
            {
                "type": "send_notification",
                "title": title,
                "description": description,
                "link": link,
                "sender_company_name": company_name,
            }
        )


        return notification