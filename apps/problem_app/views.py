from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Problem, TestCases , Category
from .serializer import ProblemSerializer, TestCasesSerializer , CategorySerializer
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
    
class AdminTestCaseCreateView(APIView):
    def post(self, request, problem_id):
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({"error": "Problem not found"}, status=404)
        
        serializer = TestCasesSerializer(data= request.data)
        if serializer.is_valid():
            serializer.save(problem=problem)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
    
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

        serializer = ProblemSerializer(paginated_queryset, many=True)
        
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
        
        serializer = ProblemSerializer(problem)
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
        
