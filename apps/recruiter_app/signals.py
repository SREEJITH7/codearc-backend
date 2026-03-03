from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.recruiter_app.models import Application
from apps.chat_app.services.notification_service import NotificationService


@receiver(post_save, sender=Application)
def notify_on_status_change(sender, instance, created, **kwargs):
    print("Signal triggered")
    print("status", instance.status)
    if not created and instance.status == "SHORTLISTED":
        NotificationService.create_and_send(
            recipient=instance.user,
            sender=instance.job.recruiter,
            notif_type="SHORTLIST",
            title="You’ve Been Shortlisted 🎉",
            description=f"You were shortlisted for {instance.job.title}",
            link="/user/applications"
        )