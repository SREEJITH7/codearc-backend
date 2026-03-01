# # apps/subscription_app/services/subscription_service.py

# from django.utils import timezone
# from apps.subscription_app.models import Subscription, SubscriptionHistory

# def get_active_subscription(user):
#     """
#     Get the user's ACTIVE subscription ONLY.
#     Returns the most recent active subscription or None.
#     """
#     return Subscription.objects.filter(
#         user=user,
#         status='ACTIVE'  # ONLY active, nothing else
#     ).first()


# def get_any_active_or_pending_subscription(user):
#     """
#     Get user's active OR pending subscription.
#     Used for blocking duplicate payments.
    
#     IMPORTANT: This EXCLUDES cancelled, expired, failed subscriptions.
#     """
#     return Subscription.objects.filter(
#         user=user,
#         status__in=['PENDING', 'ACTIVE']  # ONLY these two statuses
#     ).first()


# def get_pending_subscription(user):
#     """
#     Get user's pending subscription (checkout in progress).
#     """
#     return Subscription.objects.filter(
#         user=user,
#         status='PENDING'
#     ).first()


# def cancel_pending_subscription(user):
#     """
#     Cancel ALL pending subscriptions for user.
#     Returns (success: bool, message: str, count: int)
#     """
#     pending_subscriptions = Subscription.objects.filter(
#         user=user,
#         status='PENDING'
#     )
    
#     if not pending_subscriptions.exists():
#         return False, "No pending subscription found.", 0
    
#     try:
#         count = pending_subscriptions.count()
#         pending_subscriptions.update(status='CANCELLED')
#         return True, f"Cancelled {count} pending subscription(s).", count
#     except Exception as e:
#         return False, str(e), 0


# def activate_subscription(user, plan, stripe_subscription_id, stripe_customer_id):
#     """
#     Activate a subscription after successful Stripe payment.
#     Also handles moving old active subscription to history.
#     """
#     # Check for existing ACTIVE subscription and move to history
#     old_subscription = get_active_subscription(user)
#     if old_subscription:
#         SubscriptionHistory.objects.create(
#             user=user,
#             plan=old_subscription.plan,
#             started_at=old_subscription.start_date,
#             ended_at=timezone.now(),
#             reason='replaced'
#         )
#         old_subscription.status = 'EXPIRED'
#         old_subscription.save()
    
#     # Find and activate pending subscription
#     subscription = Subscription.objects.filter(
#         user=user,
#         status='PENDING'
#     ).first()

#     if not subscription:
#         # Create new subscription if webhook arrives first
#         subscription = Subscription.objects.create(
#             user=user,
#             plan=plan,
#             stripe_subscription_id=stripe_subscription_id,
#             stripe_customer_id=stripe_customer_id
#         )
#     else:
#         # Update pending subscription with Stripe IDs
#         subscription.stripe_subscription_id = stripe_subscription_id
#         subscription.stripe_customer_id = stripe_customer_id

#     subscription.activate()
#     return subscription


# def cancel_subscription(user):
#     """
#     Cancel user's active subscription.
#     Moves to subscription history.
#     """
#     subscription = get_active_subscription(user)
    
#     if not subscription:
#         return False, "No active subscription found."

#     try:
#         # Move to history
#         if subscription.start_date:
#             SubscriptionHistory.objects.create(
#                 user=user,
#                 plan=subscription.plan,
#                 started_at=subscription.start_date,
#                 ended_at=timezone.now(),
#                 reason='cancelled_by_user'
#             )
        
#         subscription.status = 'CANCELLED'
#         subscription.save()
        
#         return True, "Subscription cancelled successfully."
#     except Exception as e:
#         return False, str(e)


# def can_use_ai_tutor(user):
#     subscription = get_active_subscription(user)

#     if not subscription:
#         return False, {
#             "message": "No active subscription. Please upgrade to Pro to use AI Tutor.",
#             "plan": None
#         }

#     features = subscription.plan.features or {}

#     if not features.get("ai_tutor", False):
#         return False, {
#             "message": "Your current plan does not include AI Tutor. Upgrade to Pro.",
#             "plan": subscription.plan.name
#         }

#     return True, {
#         "message": "AI tutor available",
#         "plan": subscription.plan.name
#     }

# from django.utils import timezone
# from apps.recruiter_app.models import Job

# def can_post_job(user):
#     subscription = get_active_subscription(user)

#     if not subscription:
#         return False, "No active subscription."

#     features = subscription.plan.features or {}
#     job_limit = features.get("job_post_limit")

#     if not job_limit:
#         return False, "Your plan does not allow job posting."

#     # Count jobs created during this subscription period
#     current_jobs = Job.objects.filter(
#         recruiter=user,
#         created_at__gte=subscription.start_date,
#         created_at__lte=subscription.end_date
#     ).count()

#     if current_jobs >= job_limit:
#         return False, f"Job limit reached ({job_limit}). Upgrade your plan."

#     return True, "You can post jobs."

# def cleanup_expired_subscriptions():
#     """
#     Cron job to mark expired subscriptions.
#     Run this daily via Django management command or Celery.
#     """
#     now = timezone.now()
    
#     # Move ACTIVE subscriptions past end_date to GRACE
#     active_to_grace = Subscription.objects.filter(
#         status='ACTIVE',
#         end_date__lte=now
#     )
    
#     for sub in active_to_grace:
#         sub.move_to_grace()
    
#     # Expire GRACE subscriptions past grace_end_date
#     grace_to_expired = Subscription.objects.filter(
#         status='GRACE',
#         grace_end_date__lte=now
#     )
    
#     for sub in grace_to_expired:
#         SubscriptionHistory.objects.create(
#             user=sub.user,
#             plan=sub.plan,
#             started_at=sub.start_date,
#             ended_at=now,
#             reason='expired'
#         )
#         sub.expire()
    
#     # Clean up old PENDING subscriptions (older than 24 hours)
#     old_pending = Subscription.objects.filter(
#         status='PENDING',
#         created_at__lte=now - timezone.timedelta(hours=24)
#     )
    
#     cancelled_count = old_pending.update(status='CANCELLED')
    
#     return {
#         'moved_to_grace': active_to_grace.count(),
#         'expired': grace_to_expired.count(),
#         'cancelled_pending': cancelled_count
#     }

# def can_run_code(user):
#     subscription = get_active_subscription(user)

#     if not subscription:
#         return False, {
#             "message": "No active subscription. Please subscribe to run code."
#         }

#     features = subscription.plan.features or {}
#     limit = features.get("code_run_limit")

#     if not limit:
#         return False, {
#             "message": "Your current plan does not allow code execution."
#         }

#     from apps.subscription_app.models import CodeRunUsage

#     usage, created = CodeRunUsage.objects.get_or_create(
#         user=user,
#         subscription=subscription,   # 🔥 IMPORTANT FIX
#         defaults={"run_count": 0}
#     )

#     if usage.run_count >= limit:
#         return False, {
#             "message": f"Code run limit reached ({limit}). Upgrade to Pro."
#         }

#     # increment safely
#     usage.run_count += 1
#     usage.save(update_fields=["run_count"])

#     return True, {
#         "message": "Code execution allowed",
#         "runs_left": limit - usage.run_count
#     }