from rest_framework import serializers


class AdminDashboardMetricsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_recruiters = serializers.IntegerField()
    total_jobs = serializers.IntegerField()
    total_applications = serializers.IntegerField()
    active_subscriptions = serializers.IntegerField()
    total_revenue = serializers.IntegerField()