# from django.urls import path
 
# from apps.subscription_app.views.subscription_views import (
#     SubscribeView,
#     CancelSubscriptionView,
#     CurrentSubscriptionView,
#     CreatePortalSessionView
# )
# from apps.subscription_app.views.plan_views import ListPlansView
# from apps.subscription_app.views.webhook_views import StripeWebhookView


# urlpatterns = [
#     path('plans/', ListPlansView.as_view(), name='list-plans'),
#     path('subscribe/', SubscribeView.as_view(), name='subscribe'),
#     path('current/', CurrentSubscriptionView.as_view(), name='current-subscription'),
#     path('cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
#     path('portal/', CreatePortalSessionView.as_view(), name='create-portal-session'),
#     path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
# ]
from django.urls import path
 
from apps.subscription_app.views.subscription_views import (
    SubscribeView,
    CancelSubscriptionView,
    CurrentSubscriptionView,
    CreatePortalSessionView,
    CancelPendingSubscriptionView  # NEW
)
from apps.subscription_app.views.plan_views import ListPlansView
from apps.subscription_app.views.webhook_views import StripeWebhookView


urlpatterns = [
    path('plans/', ListPlansView.as_view(), name='list-plans'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('current/', CurrentSubscriptionView.as_view(), name='current-subscription'),
    path('cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
    path('cancel-pending/', CancelPendingSubscriptionView.as_view(), name='cancel-pending-subscription'),  # NEW
    path('portal/', CreatePortalSessionView.as_view(), name='create-portal-session'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
]