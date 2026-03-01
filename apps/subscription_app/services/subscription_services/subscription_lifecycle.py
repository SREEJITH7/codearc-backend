# services/subscription_services/subscription_lifecycle.py

from django.utils import timezone
from apps.subscription_app.models import Subscription, SubscriptionHistory
from .subscription_queries import get_active_subscription


def activate_subscription(user, plan, stripe_subscription_id, stripe_customer_id):
    old_subscription = get_active_subscription(user)

    if old_subscription:
        SubscriptionHistory.objects.create(
            user=user,
            plan=old_subscription.plan,
            started_at=old_subscription.start_date,
            ended_at=timezone.now(),
            reason="replaced"
        )
        old_subscription.status = "EXPIRED"
        old_subscription.save()

    subscription = Subscription.objects.filter(
        user=user,
        status="PENDING"
    ).first()

    if not subscription:
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            stripe_subscription_id=stripe_subscription_id,
            stripe_customer_id=stripe_customer_id
        )
    else:
        subscription.stripe_subscription_id = stripe_subscription_id
        subscription.stripe_customer_id = stripe_customer_id

    subscription.activate()
    return subscription


def cancel_subscription(user):
    subscription = get_active_subscription(user)

    if not subscription:
        return False, "No active subscription found."

    SubscriptionHistory.objects.create(
        user=user,
        plan=subscription.plan,
        started_at=subscription.start_date,
        ended_at=timezone.now(),
        reason="cancelled_by_user"
    )

    subscription.status = "CANCELLED"
    subscription.save()

    return True, "Subscription cancelled successfully."