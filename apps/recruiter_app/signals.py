from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.recruiter_app.models import Application
from apps.chat_app.services.notification_service import NotificationService


@receiver(post_save, sender=Application)
def notify_on_status_change(sender, instance, created, **kwargs):
    print("Signal triggered")
    print("status", instance.status)
    
    if created:
        return

    notif_data = None
    if instance.status == "SHORTLISTED":
        notif_data = {
            "notif_type": "SHORTLIST",
            "title": "You’ve Been Shortlisted 🎉",
            "description": f"You were shortlisted for {instance.job.title}",
        }
    elif instance.status == "REJECTED":
        notif_data = {
            "notif_type": "REJECTION",
            "title": "Application Status Update",
            "description": f"Unfortunately, your application for {instance.job.title} was not selected.",
        }
    elif instance.status == "ACCEPTED":
        notif_data = {
            "notif_type": "OFFER",
            "title": "Offer Received! 🎊",
            "description": f"You have received an offer for {instance.job.title}",
        }

    if notif_data:
        NotificationService.create_and_send(
            recipient=instance.user,
            sender=instance.job.recruiter,
            notif_type=notif_data["notif_type"],
            title=notif_data["title"],
            description=notif_data["description"],
            link="/user/applications"
        )