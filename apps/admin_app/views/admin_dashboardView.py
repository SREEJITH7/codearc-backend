from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from auth_app.models import User
from recruiter_app.models import Job, Application
from subscription_app.models import Subscription

class AdminDashboardMetricsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = User.objects.filter(role="user").count()
        total_recruiters = User.objects.filter(role="recruiter").count()
        total_jobs = Job.objects.count()
        total_applications = Application.objects.count()

        active_subscriptions = Subscription.objects.filter(status="active").count()

        total_revenue = sum(
            Subscription.objects.filter(status="active")
            .values_list("amount", flat=True)
        )

        data = {
            "total_users": total_users,
            "total_recruiters": total_recruiters,
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "active_subscriptions": active_subscriptions,
            "total_revenue": total_revenue,
        }

        return Response(data)