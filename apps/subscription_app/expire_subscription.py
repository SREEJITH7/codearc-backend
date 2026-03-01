from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.subscription_app.models import Subscription
from apps.subscription_app.services.subscription_service import _archive_subscription


class Command(BaseCommand):
    help = 'Expire subscriptions past grace period'

    def handle(self, *args, **kwargs):
        now = timezone.now()

        # Move ACTIVE → GRACE when end_date passes
        active_expired = Subscription.objects.filter(
            status='ACTIVE',
            end_date__lt=now
        )
        for sub in active_expired:
            sub.status = 'GRACE'
            sub.save()
            self.stdout.write(f"Moved to GRACE: {sub.user}")

         
        grace_expired = Subscription.objects.filter(
            status='GRACE',
            grace_end_date__lt=now
        )
        for sub in grace_expired:
            _archive_subscription(sub, reason='expired')
            sub.status = 'EXPIRED'
            sub.save()
            self.stdout.write(f"Expired: {sub.user}")

        self.stdout.write(self.style.SUCCESS('Subscription expiry check complete.'))