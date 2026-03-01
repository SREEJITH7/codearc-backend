import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.subscription_app.models import Subscription
class StripeWebhookView(APIView):

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        print("🔔 Webhook received!", sig_header)
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
            print("✅ Event verified:", event['type'])
        except Exception as e:
            print("❌ Webhook error:", e)
            return Response({"error": "Invalid webhook"}, status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Get subscription_id from metadata you set during checkout creation
            subscription_id = session.get('metadata', {}).get('subscription_id')
            # The real Stripe subscription ID (sub_xxx)
            stripe_sub_id = session.get('subscription')

            if subscription_id:
                try:
                    subscription = Subscription.objects.get(id=subscription_id)
                    
                    # Update to real Stripe subscription ID for future webhook lookups
                    subscription.stripe_subscription_id = stripe_sub_id
                    subscription.payment_status = 'paid'
                    subscription.activate()  # sets status → ACTIVE

                    # Cancel any other stale PENDING subscriptions for this user
                    Subscription.objects.filter(
                        user=subscription.user,
                        status='PENDING'
                    ).exclude(id=subscription.id).update(status='CANCELLED')

                except Subscription.DoesNotExist:
                    pass

        elif event['type'] == 'invoice.payment_succeeded':
            # Now this works correctly because stripe_subscription_id is sub_xxx
            stripe_sub_id = event['data']['object']['subscription']
            try:
                subscription = Subscription.objects.get(
                    stripe_subscription_id=stripe_sub_id
                )
                subscription.payment_status = 'paid'
                subscription.activate()
            except Subscription.DoesNotExist:
                pass

        elif event['type'] == 'invoice.payment_failed':
            stripe_sub_id = event['data']['object']['subscription']
            try:
                subscription = Subscription.objects.get(
                    stripe_subscription_id=stripe_sub_id
                )
                subscription.payment_status = 'failed'
                subscription.move_to_grace()
            except Subscription.DoesNotExist:
                pass

        elif event['type'] == 'customer.subscription.deleted':
            stripe_sub_id = event['data']['object']['id']
            try:
                subscription = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
                subscription.expire()
            except Subscription.DoesNotExist:
                pass

        elif event['type'] == 'customer.subscription.updated':
            data = event['data']['object']
            stripe_sub_id = data['id']
            try:
                subscription = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
                if data.get('cancel_at_period_end'):
                    subscription.status = 'CANCELLED'
                    subscription.save()
            except Subscription.DoesNotExist:
                pass

        return Response({"status": "ok"})