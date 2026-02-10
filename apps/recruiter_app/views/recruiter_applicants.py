from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.paginator import Paginator

from apps.recruiter_app.models import Application
from apps.recruiter_app.utils.coding_stats import calculate_coding_stats


class RecruiterApplicantsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recruiter = request.user

        # 1️⃣ Base queryset (FAST: DB does filtering)
        qs = Application.objects.filter(
            job__recruiter=recruiter
        ).select_related("job", "user").order_by("-created_at")

        # Optional filters
        if job_id := request.query_params.get("job_id"):
            qs = qs.filter(job_id=job_id)

        if status_filter := request.query_params.get("status"):
            qs = qs.filter(status=status_filter.upper())

        # 2️⃣ Pagination FIRST (VERY IMPORTANT)
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 5))

        paginator = Paginator(qs, limit)
        current_page = paginator.get_page(page)

        temp_results = []

        # 3️⃣ Compute stats ONLY for visible applicants
        for app in current_page.object_list:
            stats = calculate_coding_stats(app.user) if app.user else {}

            temp_results.append({
                "id": app.id,
                "applicant_name": app.name,
                "email": app.email,
                "contactNo": app.contactNo,
                "job_title": app.job.title,
                "status": app.status,
                "created_at": app.created_at,
                "coding_stats": stats,
            })

        # 4️⃣ Sort by coding score (LOCAL ranking)
        temp_results.sort(
            key=lambda x: x["coding_stats"].get("score", 0),
            reverse=True
        )

        # 5️⃣ Assign LOCAL rank
        start_rank = (page - 1) * limit

        for index, item in enumerate(temp_results, start=1):
            item["coding_stats"]["rank"] = start_rank + index


        return Response({
            "success": True,
            "data": {
                "applications": temp_results,
                "pagination": {
                    "page": page,
                    "pages": paginator.num_pages,
                    "total": paginator.count,
                    "limit": limit,
                }
            }
        }, status=status.HTTP_200_OK)
