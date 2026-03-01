# services/subscription_services/feature_job.py

from apps.recruiter_app.models import Job
from .subscription_queries import get_active_subscription


def can_post_job(user):
    subscription = get_active_subscription(user)

    if not subscription:
        return False, "No active subscription."

    features = subscription.plan.features or {}
    limit = features.get("job_post_limit")

    if not limit:
        return False, "Job posting not allowed."

    current_jobs = Job.objects.filter(
        recruiter=user,
        created_at__gte=subscription.start_date,
        created_at__lte=subscription.end_date
    ).count()

    if current_jobs >= limit:
        return False, f"Job limit reached ({limit})."

    return True, "Allowed"