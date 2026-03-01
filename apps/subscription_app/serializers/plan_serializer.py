from rest_framework import serializers
from apps.subscription_app.models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'role_type', 'price', 'duration_days', 'features']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'status', 'start_date', 'end_date', 'grace_end_date', 'days_remaining']

    def get_days_remaining(self, obj):
        from django.utils import timezone
        remaining = obj.end_date - timezone.now()
        return max(remaining.days, 0)