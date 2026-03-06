from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.paginator import Paginator

from django.db.models import Q
from apps.recruiter_app.models import Application
from apps.recruiter_app.utils.coding_stats import calculate_coding_stats
from .permissions import IsAdmin



class AdminApplicationListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        try:
            # 1️⃣ Base queryset with recruiter info
            qs = Application.objects.select_related(
                "job", "user", "job__recruiter"
            ).order_by("-created_at")

            # Optional filters
            if recruiter_id := request.query_params.get("recruiter_id"):
                qs = qs.filter(job__recruiter_id=recruiter_id)

            if job_id := request.query_params.get("job_id"):
                qs = qs.filter(job_id=job_id)

            if status_filter := request.query_params.get("status"):
                qs = qs.filter(status=status_filter.upper())

            if search := request.query_params.get("search"):
                qs = qs.filter(
                    Q(name__icontains=search) | 
                    Q(email__icontains=search)
                )

            # 2️⃣ Pagination
            try:
                page = int(request.query_params.get("page", 1))
                limit = int(request.query_params.get("limit", 10))
            except (ValueError, TypeError):
                page = 1
                limit = 10

            paginator = Paginator(qs, limit)
            current_page = paginator.get_page(page)

            results = []

            # 3️⃣ Include recruiter info and coding stats
            for app in current_page.object_list:
                try:
                    stats = calculate_coding_stats(app.user) if app.user else {}
                except Exception as stats_err:
                    print(f"Error calculating stats for user {app.user.id}: {stats_err}")
                    stats = {}

                results.append({
                    "id": app.id,
                    "applicant_name": app.name,
                    "email": app.email,
                    "contactNo": app.contactNo,
                    "job_title": app.job.title,
                    "recruiter_name": app.job.recruiter.username,
                    "recruiter_id": app.job.recruiter.id,
                    "status": app.status,
                    "created_at": app.created_at,
                    "coding_stats": stats,
                })

            return Response({
                "success": True,
                "data": {
                    "applications": results,
                    "pagination": {
                        "page": page,
                        "pages": paginator.num_pages,
                        "total": paginator.count,
                        "limit": limit,
                        "has_next": current_page.has_next(),
                        "has_previous": current_page.has_previous(),
                    }
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": "Failed to fetch applications. Please try again.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminDashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        try:
            from django.contrib.auth import get_user_model
            from apps.recruiter_app.models import Job, Application
            from apps.subscription_app.models import Subscription
            from django.db.models import Sum

            User = get_user_model()

            total_users = User.objects.filter(role="user").count()
            total_recruiters = User.objects.filter(role="recruiter").count()
            total_jobs = Job.objects.count()
            total_applications = Application.objects.count()
            active_subscriptions = Subscription.objects.filter(status="ACTIVE").count()
            
            # Aggregate revenue from active subscriptions
            total_revenue_data = Subscription.objects.filter(status="ACTIVE").aggregate(
                total_revenue=Sum("plan__price")
            )
            total_revenue = total_revenue_data.get("total_revenue") or 0

            return Response({
                "total_users": total_users,
                "total_recruiters": total_recruiters,
                "total_jobs": total_jobs,
                "total_applications": total_applications,
                "active_subscriptions": active_subscriptions,
                "total_revenue": float(total_revenue)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in AdminDashboardMetricsView: {e}")
            return Response({
                "success": False,
                "message": "Failed to fetch dashboard metrics",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







