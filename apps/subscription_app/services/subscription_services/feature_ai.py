# services/subscription_services/feature_ai.py

from .subscription_queries import get_active_subscription


def can_use_ai_tutor(user):
    subscription = get_active_subscription(user)

    if not subscription:
        return False, {"message": "No active subscription."}

    features = subscription.plan.features or {}

    if not features.get("ai_tutor"):
        return False, {"message": "AI Tutor not included in your plan."}

    return True, {"message": "AI Tutor available"}