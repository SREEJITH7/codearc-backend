from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.recruiter_app.models import Application
from apps.chat_app.models import Conversation
from apps.chat_app.services.notification_service import NotificationService

@receiver(post_save, sender=Application)
def notify_on_status_change(sender, instance, created, **kwargs):
    print("Signal triggered")
    print("status", instance.status)
    
    if created:
        return

    notif_data = None

    if instance.status in ["SHORTLISTED", "ACCEPTED"]:
        # Create or Get Conversation
        Conversation.objects.get_or_create(
            application=instance,
            defaults={
                'user': instance.user,
                'recruiter': instance.job.recruiter
            }
        )
        
        if instance.status == "SHORTLISTED":
            notif_data = {
                "notif_type": "SHORTLIST",
                "title": "You've Been Shortlisted 🎉",
                "description": f"You were shortlisted for {instance.job.title}",
            }
        else:  # ACCEPTED
            notif_data = {
                "notif_type": "OFFER",
                "title": "Offer Received! 🎊",
                "description": f"You have received an offer for {instance.job.title}",
            }

    elif instance.status == "REJECTED":
        notif_data = {
            "notif_type": "REJECTION",
            "title": "Application Update",
            "description": f"Your application for {instance.job.title} was not selected.",
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