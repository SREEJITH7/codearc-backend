from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Problem, TestCases, Category, Submission
from .serializer import ProblemSerializer, TestCasesSerializer, CategorySerializer
from .execution import run_code
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)


class AdminProblemCreateView(APIView):
    def post(self , request):
        title = request.data.get('title')
        if title and Problem.objects.filter(title__iexact=title).exists():
             return Response({"message": "This problem is already added"}, status=status.HTTP_400_BAD_REQUEST)

        serialiser = ProblemSerializer(data= request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        logger.error(f"Validation Errors: {serialiser.errors}")
        return Response(serialiser.errors, status= status.HTTP_400_BAD_REQUEST)
    


class ProblemUpdateView(APIView):
    def put(self,request, problem_id):
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({'error':"problem not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProblemSerializer(problem, data=request.data,partial= True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True, "message" : "Problem updated successfully", "data": serializer.data,
            },status=status.HTTP_200_OK)
            
        logger.error(f"Validation Errors:{serializer.errors}")
        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    
    
class ProblemListView(APIView):
    def get(self, request):
        queryset = Problem.objects.select_related("category").all().order_by("id")

        
        difficulty = request.query_params.get("difficulty")
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty.upper())

        
        tag = request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(tags__icontains=tag)

        paginator = ProblemPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        solved_ids = set()
        if request.user.is_authenticated:
            solved_ids = set(Submission.objects.filter(
                user=request.user, 
                status="Accepted"
            ).values_list("problem_id", flat=True))

        serializer = ProblemSerializer(
            paginated_queryset, 
            many=True, 
            context={'request': request, 'solved_problem_ids': solved_ids}
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
            return Response({"error": "Problem not fouond"}, status=404)
        
        solved_ids = set()
        if request.user.is_authenticated:
            if Submission.objects.filter(user=request.user, problem=problem, status="Accepted").exists():
                solved_ids.add(problem.id)
        
        serializer = ProblemSerializer(problem, context={'solved_problem_ids': solved_ids})
        return Response(serializer.data)

class ProblemToggleView(APIView):
    def patch(self, request, problem_id):
        try:
            problem = Problem.objects.get(id=problem_id)
            problem.is_active = not problem.is_active
            problem.save()
            
            serializer = ProblemSerializer(problem)
            return Response({
                "success": True,
                "message": f"Problem {'activated' if problem.is_active else 'deactivated'} successfully",
                "data": serializer.data
            })
        except Problem.DoesNotExist:
            return Response({
                "success": False,
                "message": "Problem not found"
            }, status=status.HTTP_404_NOT_FOUND)
    
    
class ProblemDeleteView(APIView):
    def delete(self, request, problem_id):
        try:
            problem = Problem.objects.get(id=problem_id)
            problem.delete()
            return Response({
                "success": True,
                "message": "Problem deleted successfully"
            }, status=status.HTTP_200_OK)
        except Problem.DoesNotExist:
            return Response({
                "success": False,
                "message": "Problem not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProblemPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50




class CategoryListView(APIView):
    def get(self, request):
        search = request.query_params.get("search", "").strip()

        queryset = Category.objects.all().order_by("name")

        if search:
            queryset = queryset.filter(name__icontains=search)

        paginator = ProblemPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = CategorySerializer(paginated_queryset, many=True)

        # Get pagination info
        page_obj = paginator.page
        
        return Response({
            "success": True,
            "data": {
                "categories": serializer.data,
                "pagination": {
                    "count": paginator.page.paginator.count,
                    "pages": paginator.page.paginator.num_pages,
                    "current": paginator.page.number,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                }
            }
        })


class CategoryCreateView(APIView):
    def post(self, request):
        try:
            name = request.data.get('name')
            
            if not name:
                return Response({
                    "success": False,
                    "message": "Category name is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create slug from name
            slug = slugify(name)
            
            # Check if category already exists
            if Category.objects.filter(name__iexact=name).exists():
                return Response({
                    "success": False,
                    "message": "Category already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create category with Active status by default
            category = Category.objects.create(
                name=name,
                slug=slug,
                status='Active'  # ✅ Default to Active
            )
            
            serializer = CategorySerializer(category)
            
            return Response({
                "success": True,
                "message": "Category created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    



class CategoryUpdateView(APIView):
    """
    PUT /admin/updatecategory/<category_id>/ - Update category
    """
    def put(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({
                "success": False,
                "message": "Category not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        name = request.data.get('name')
        if not name:
            return Response({
                "success": False,
                "message": "Category name is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if another category with this name exists
        if Category.objects.filter(name__iexact=name).exclude(id=category_id).exists():
            return Response({
                "success": False,
                "message": "Category with this name already exists"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update slug
        from django.utils.text import slugify
        slug = slugify(name)
        
        serializer = CategorySerializer(category, data={
            'name': name,
            'slug': slug
        })
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Category updated successfully",
                "data": serializer.data
            })
        
        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CategoryToggleView(APIView):
    def patch(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
            # Toggle the status
            if category.status == 'Active':
                category.status = 'InActive'
            else:
                category.status = 'Active'
            
            category.save()
            
            serializer = CategorySerializer(category)
            
            return Response({
                "success": True,
                "message": f"Category {category.status.lower()} successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Category.DoesNotExist:
            return Response({
                "success": False,
                "message": "Category not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST) 
        
class RunCodeView(APIView):
    def post(self, request):
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        language = request.data.get("language")

        if not all([problem_id, code, language]):
            return Response(
                {"success": False, "message": "Missing fields"},
                status=status.HTTP_400_BAD_REQUEST
            )


        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response(
                {"success": False, "message": "Problem not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        testcases = TestCases.objects.filter(problem=problem).order_by("order")

        results, console, memory_usage = run_code(
            language,
            code,
            testcases,
            problem.function_name
        )

        overall_status = (
            "Accepted" if results and all(r["passed"] for r in results)
            else "Wrong Answer"
        )

        return Response({
            "success": True,
            "overallStatus": overall_status,
            "testResults": results,
            "consoleOutput": console,
            "memory": round(memory_usage, 2),
            "runtime": round(sum(r.get("runtime", 0.0) for r in results), 2)
        })


class SubmitCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        language = request.data.get("language")

        if not all([problem_id, code, language]):
            return Response({"success": False, "message": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({"success": False, "message": "Problem not found"}, status=status.HTTP_404_NOT_FOUND)

        testcases = TestCases.objects.filter(problem=problem).order_by("order")

        # Run the code
        results, console, memory_usage = run_code(language, code, testcases, problem.function_name)

        if not results and console:
            status_value = "Runtime Error"
            passed = 0
            total = testcases.count()
            total_runtime = 0.0
            memory_usage = 0.0
        else:
            passed = sum(1 for r in results if r.get("passed", False))
            total = len(results)
            total_runtime = sum(r.get("runtime", 0.0) for r in results)
            status_value = "Accepted" if passed == total else "Wrong Answer"
            memory_usage = round(memory_usage, 2)

        # Update or create submission
        submission, created = Submission.objects.update_or_create(
            user=user,
            problem=problem,
            defaults={
                "language": language,
                "code": code,
                "status": status_value,
                "passed_count": passed,
                "total_count": total,
                "runtime": total_runtime,
                "memory": memory_usage,
            }
        )

        # Update problem stats if first time submission
        if created:
            problem.total_submissions += 1
            problem.save()

        # Calculate basic percentiles
        all_submissions = Submission.objects.filter(problem=problem, status="Accepted")
        total_accepted = all_submissions.count()
        
        if total_accepted > 1:
            slower_submissions = all_submissions.filter(runtime__gt=total_runtime).count()
            runtime_percentile = round((slower_submissions / total_accepted) * 100, 2)
            
            larger_memory = all_submissions.filter(memory__gt=memory_usage).count()
            memory_percentile = round((larger_memory / total_accepted) * 100, 2)
        else:
            runtime_percentile = 100.0
            memory_percentile = 100.0

        return Response({
            "success": True,
            "submission_id": submission.id,
            "overallStatus": status_value,
            "passed": passed,
            "total": total,
            "runtime": round(total_runtime, 2),
            "memory": memory_usage,
            "runtime_percentile": runtime_percentile,
            "memory_percentile": memory_percentile,
            "consoleOutput": console,
            "testResults": results
        })

class UserSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, problem_id):
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({"success": False, "message": "Problem not found"}, status=404)

        submissions = Submission.objects.filter(
            problem=problem, 
            user=request.user
        ).order_by("-created_at")
        
        data = []
        for sub in submissions:
            data.append({
                "id": sub.id,
                "status": sub.status,
                "runtime": sub.runtime,
                "memory": sub.memory,
                "language": sub.language,
                "code": sub.code,
                "created_at": sub.created_at,
                "passed_count": sub.passed_count,
                "total_count": sub.total_count,
                "accuracy": round((sub.passed_count / sub.total_count * 100), 1) if sub.total_count > 0 else 0
            })

        return Response({
            "success": True,
            "data": data
        })

class AllSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, problem_id):
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({"success": False, "message": "Problem not found"}, status=404)

        submissions = Submission.objects.filter(problem=problem, status="Accepted").order_by("-created_at")
        
        data = []
        for sub in submissions:
            data.append({
                "id": sub.id,
                "status": sub.status,
                "runtime": sub.runtime,
                "memory": sub.memory,
                "language": sub.language,
                "created_at": sub.created_at,
                "passed_count": sub.passed_count,
                "total_count": sub.total_count,
            })

        return Response(data)