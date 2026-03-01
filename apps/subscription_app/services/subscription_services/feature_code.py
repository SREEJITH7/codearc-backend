# services/subscription_services/feature_code.py

from apps.subscription_app.models import CodeRunUsage
from .subscription_queries import get_active_subscription


def can_run_code(user):
    subscription = get_active_subscription(user)

    if not subscription:
        return False, {"message": "No active subscription."}

    features = subscription.plan.features or {}
    limit = features.get("code_run_limit")

    if not limit:
        return False, {"message": "Code execution not allowed."}

    usage, _ = CodeRunUsage.objects.get_or_create(
        user=user,
        subscription=subscription,
        defaults={"run_count": 0}
    )

    if usage.run_count >= limit:
        return False, {"message": "Code run limit reached."}

    usage.run_count += 1
    usage.save(update_fields=["run_count"])

    return True, {"runs_left": limit - usage.run_count}