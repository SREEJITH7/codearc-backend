from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Problem, Submission
from ..serializers import ProblemSerializer
from rest_framework.pagination import PageNumberPagination


class ProblemPagination(PageNumberPagination):
    page_size = 10


class ProblemListView(APIView):
    def get(self, request):
        try:
            queryset = Problem.objects.select_related("category").order_by("id")
            queryset = queryset.exclude(category__status="InActive")

            difficulty = request.query_params.get("difficulty")
            if difficulty:
                queryset = queryset.filter(difficulty=difficulty.upper())

            tag = request.query_params.get("tag")
            if tag:
                queryset = queryset.filter(tags__icontains=tag)

            paginator = ProblemPagination()
            try:
                page = paginator.paginate_queryset(queryset, request)
            except Exception as pag_err:
                print(f"Pagination error in ProblemListView: {pag_err}")
                return Response({
                    "success": False,
                    "message": "Invalid page number or pagination error"
                }, status=400)

            solved_ids = set()
            if request.user.is_authenticated:
                try:
                    solved_ids = set(
                        Submission.objects.filter(user=request.user, status="Accepted")
                        .values_list("problem_id", flat=True)
                    )
                except Exception as sub_err:
                    print(f"Error fetching solved status: {sub_err}")
                    # Not critical, continue without solved status

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
        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while fetching problems",
                "error": str(e)
            }, status=500)


class ProblemDetailView(APIView):
    def get(self, request, problem_id):
        try:
            try:
                problem = Problem.objects.get(id=problem_id)
            except Problem.DoesNotExist:
                return Response({"success": False, "message": "Problem not found"}, status=404)
            except (ValueError, TypeError):
                 return Response({"success": False, "message": "Invalid problem ID format"}, status=400)

            solved_ids = set()
            if request.user.is_authenticated:
                try:
                    if Submission.objects.filter(
                        user=request.user, problem=problem, status="Accepted"
                    ).exists():
                        solved_ids.add(problem.id)
                except Exception as sub_err:
                    print(f"Error checking solved status for detail view: {sub_err}")

            serializer = ProblemSerializer(problem, context={"solved_problem_ids": solved_ids})
            return Response(serializer.data)
        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while fetching problem details",
                "error": str(e)
            }, status=500)
