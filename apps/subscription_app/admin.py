from django.contrib import admin
from .models import Plan, Subscription, SubscriptionHistory

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_type', 'price', 'duration_days', 'stripe_price_id', 'is_active')
    list_filter = ('role_type', 'is_active')
    search_fields = ('name', 'stripe_price_id')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'plan')
    search_fields = ('user__email', 'stripe_subscription_id')

@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'started_at', 'ended_at', 'reason')
