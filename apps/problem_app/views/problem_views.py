from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Problem, Submission
from ..serializers import ProblemSerializer
from rest_framework.pagination import PageNumberPagination


class ProblemPagination(PageNumberPagination):
    page_size = 10


class ProblemListView(APIView):
    def get(self, request):
        queryset = Problem.objects.select_related("category").order_by("id")
        queryset = queryset.exclude(category__status="InActive")

        difficulty = request.query_params.get("difficulty")
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty.upper())

        tag = request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(tags__icontains=tag)

        paginator = ProblemPagination()
        page = paginator.paginate_queryset(queryset, request)

        solved_ids = set()
        if request.user.is_authenticated:
            solved_ids = set(
                Submission.objects.filter(user=request.user, status="Accepted")
                .values_list("problem_id", flat=True)
            )

        serializer = ProblemSerializer(
            page,
            many=True,
            context={"solved_problem_ids": solved_ids}
        )

        return Response({
            "success": True,
            "data": {
                "problems": serializer.data,
                "pagination": {
                    "count": paginator.page.paginator.count,
                    "pages": paginator.page.paginator.num_pages,
                    "current": paginator.page.number,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                }
            }
        })


class ProblemDetailView(APIView):
    def get(self, request, problem_id):
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({"message": "Problem not found"}, status=404)

        solved_ids = set()
        if request.user.is_authenticated and Submission.objects.filter(
            user=request.user, problem=problem, status="Accepted"
        ).exists():
            solved_ids.add(problem.id)

        serializer = ProblemSerializer(problem, context={"solved_problem_ids": solved_ids})
        return Response(serializer.data)
