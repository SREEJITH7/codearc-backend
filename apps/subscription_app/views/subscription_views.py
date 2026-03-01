
from urllib import request

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import stripe

from apps.subscription_app.models import Plan, Subscription
from apps.subscription_app.serializers.plan_serializer import SubscriptionSerializer
from apps.subscription_app.services.subscription_services import (
    get_active_subscription,
    get_any_active_or_pending_subscription,
    activate_subscription,
    cancel_subscription,
    can_use_ai_tutor,
    can_post_job,
)

from apps.subscription_app.services.stripe_service import (
    create_stripe_customer,
    create_stripe_subscription,
    create_stripe_portal_session,
    create_stripe_checkout_session,
)


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]
       

    def post(self, request):
        plan_id = request.data.get('plan_id')

        if not plan_id:
            return Response(
                {"error": "plan_id is required."},
                status=400
            )

        try:
            plan = Plan.objects.get(id=plan_id, is_active=True)
        except Plan.DoesNotExist:
            return Response(
                {"error": "Plan not found."},
                status=404
            )

         
        existing_subscription = get_any_active_or_pending_subscription(request.user)

        if existing_subscription:
            if existing_subscription.status == 'PENDING':
                return Response(
                    {
                        "error": "You have a pending subscription. Please complete or cancel it first.",
                        "current_plan": existing_subscription.plan.name,
                        "status": existing_subscription.status,
                        "subscription_id": existing_subscription.id
                    },
                    status=400
                )
            else:  # ACTIVE
                return Response(
                    {
                        "error": "You already have an active subscription.",
                        "current_plan": existing_subscription.plan.name,
                        "status": existing_subscription.status
                    },
                    status=400
                )

        # Create/Get Stripe customer
        customer_id = create_stripe_customer(request.user)

        success_url = "http://localhost:5173/user/profile?showSubscriptionSuccess=true"
        cancel_url = "http://localhost:5173/user/profile"

        try:
            # Create PENDING subscription record BEFORE checkout
            pending_subscription = Subscription.objects.create(
                user=request.user,
                plan=plan,
                status='PENDING',
                stripe_customer_id=customer_id
            )

            # Create Stripe checkout session with metadata
            checkout_session = create_stripe_checkout_session(
                customer_id,
                plan.stripe_price_id,
                success_url,
                cancel_url,
                metadata={
                    'subscription_id': str(pending_subscription.id),
                    'user_id': str(request.user.id),
                    'plan_id': str(plan.id)
                }
            )
            
            # Save stripe session ID for reference
            pending_subscription.stripe_subscription_id = checkout_session.id
            pending_subscription.save()

            return Response({
                "message": "Checkout session created.",
                "checkout_url": checkout_session.url,
                "subscription_id": pending_subscription.id
            }, status=201)
        except Exception as e:
            # If checkout creation fails, delete the pending subscription
            if 'pending_subscription' in locals():
                pending_subscription.delete()
            
            return Response({"error": str(e)}, status=400)
    

class CurrentSubscriptionView(APIView):
    """
    GET /subscription/current/
    Returns ACTIVE subscription only (not pending)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscription = get_active_subscription(request.user)

        if not subscription:
            # Check if there's a pending subscription
            pending = Subscription.objects.filter(
                user=request.user,
                status='PENDING'
            ).first()

            if pending:
                return Response(
                    {
                        "message": "Payment pending.", 
                        "subscription": None,
                        "pending_subscription": {
                            "plan_name": pending.plan.name,
                            "status": "PENDING",
                            "created_at": pending.created_at,
                            "subscription_id": pending.id
                        }
                    },
                    status=status.HTTP_200_OK
                )

            return Response(
                {"message": "No active subscription.", "subscription": None},
                status=status.HTTP_200_OK
            )

        serializer = SubscriptionSerializer(subscription)

        feature_access = {}
        if request.user.role == 'USER':
            allowed, info = can_use_ai_tutor(request.user)
            feature_access['ai_tutor'] = {
                "allowed": allowed,
                **info
            }
        elif request.user.role == 'RECRUITER':
            allowed, message = can_post_job(request.user)
            feature_access['can_post_job'] = allowed
            feature_access['job_limit_message'] = message

        response_data = {
            "subscription": serializer.data,
            "current_subscription": {
                "plan_id": subscription.plan.id,
                "plan_name": subscription.plan.name,
                "status": subscription.status,
            },
            "feature_access": feature_access
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CancelSubscriptionView(APIView):
    """
    POST /subscription/cancel/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        success, message = cancel_subscription(request.user)

        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)

        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


class CancelPendingSubscriptionView(APIView):
    """
    POST /subscription/cancel-pending/
    Cancel a pending subscription (abandoned checkout)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Find ALL pending subscriptions for this user
        pending_subscriptions = Subscription.objects.filter(
            user=request.user,
            status='PENDING'
        )

        if not pending_subscriptions.exists():
            return Response(
                {"error": "No pending subscription found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Cancel all pending subscriptions (in case there are multiple)
        count = pending_subscriptions.count()
        pending_subscriptions.update(status='CANCELLED')

        return Response(
            {
                "message": f"Cancelled {count} pending subscription(s).",
                "count": count
            },
            status=status.HTTP_200_OK
        )


class CreatePortalSessionView(APIView):
    """
    POST /subscription/portal/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subscription = Subscription.objects.filter(user=request.user).first()
        if not subscription or not subscription.stripe_customer_id:
            return Response(
                {"error": "No subscription or customer found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            portal_session = create_stripe_portal_session(
                subscription.stripe_customer_id,
                "http://localhost:5173/user/subscription"
            )
            return Response({"url": portal_session.url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)