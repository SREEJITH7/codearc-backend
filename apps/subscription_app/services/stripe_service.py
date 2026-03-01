

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_customer(user):
    """
    Create a Stripe customer for the user
    """
    customer = stripe.Customer.create(
        email=user.email,
        name=user.get_full_name(),
        metadata={
            'user_id': str(user.id),
            'role': user.role
        }
    )
    return customer.id

def create_stripe_subscription(customer_id, stripe_price_id):
    """
    Create a Stripe subscription (alternative method, not used in checkout flow)
    """
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": stripe_price_id}],
        payment_behavior='default_incomplete',
        expand=['latest_invoice.payment_intent'],
    )
    return subscription

def cancel_stripe_subscription(stripe_subscription_id):
    """
    Cancel a Stripe subscription immediately
    """
    return stripe.Subscription.delete(stripe_subscription_id)

def create_stripe_portal_session(customer_id, return_url):
    """
    Create Stripe billing portal session for customer to manage subscription
    """
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session

def create_stripe_checkout_session(customer_id, stripe_price_id, success_url, cancel_url, metadata=None):
    """
    Create Stripe checkout session with optional metadata
    
    Args:
        customer_id: Stripe customer ID
        stripe_price_id: Stripe price ID for the plan
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if checkout is cancelled
        metadata: Dict of metadata to attach (e.g., subscription_id, user_id, plan_id)
    
    Returns:
        Stripe checkout session object
    """
    session_params = {
        'customer': customer_id,
        'payment_method_types': ['card'],
        'line_items': [{
            'price': stripe_price_id,
            'quantity': 1,
        }],
        'mode': 'subscription',
        'success_url': success_url,
        'cancel_url': cancel_url,
    }
    
    # Add metadata if provided (helps track which subscription to activate)
    if metadata:
        session_params['metadata'] = metadata
        session_params['subscription_data'] = {'metadata': metadata}
    
    session = stripe.checkout.Session.create(**session_params)
    return session