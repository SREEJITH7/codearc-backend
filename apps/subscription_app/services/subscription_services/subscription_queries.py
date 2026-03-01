# services/subscription_services/subscription_queries.py

from apps.subscription_app.models import Subscription

def get_active_subscription(user):
    return Subscription.objects.filter(
        user=user,
        status="ACTIVE"
    ).first()


def get_pending_subscription(user):
    return Subscription.objects.filter(
        user=user,
        status="PENDING"
    ).first()


def get_any_active_or_pending_subscription(user):
    return Subscription.objects.filter(
        user=user,
        status__in=["PENDING", "ACTIVE"]
    ).first()