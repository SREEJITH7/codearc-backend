from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.text import slugify
from ..models import Category
from ..serializers import CategorySerializer
from rest_framework.pagination import PageNumberPagination



class CategoryPagination(PageNumberPagination):
    page_size = 10


from django.db.models import Count # Added import

# ... (existing code)

class CategoryListView(APIView):
    def get(self, request):
        try:
            # Annotate with problem count
            queryset = Category.objects.annotate(problem_count=Count('problems')).order_by("name")
            search = request.query_params.get("search")

            if search:
                queryset = queryset.filter(name__icontains=search)

            paginator = CategoryPagination()
            try:
                page = paginator.paginate_queryset(queryset, request)
            except Exception as pag_err:
                print(f"Pagination error in CategoryListView: {pag_err}")
                return Response({
                    "success": False,
                    "message": "Invalid page number or pagination error"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = CategorySerializer(page, many=True)
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
        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while fetching categories",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryCreateView(APIView):
    def post(self, request):
        try:
            name = request.data.get("name")
            if not name:
                return Response({
                    "success": False,
                    "message": "Name is required"
                }, status=status.HTTP_400_BAD_REQUEST)

            if Category.objects.filter(name__iexact=name).exists():
                return Response({
                    "success": False,
                    "message": "Category with this name already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            category = Category.objects.create(
                name=name,
                slug=slugify(name),
                status="Active"
            )
            
            return Response({
                "success": True,
                "data": CategorySerializer(category).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "message": "Failed to create category",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryUpdateView(APIView):
    def put(self, request, category_id):
        try:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Category not found"
                }, status=status.HTTP_404_NOT_FOUND)
            except (ValueError, TypeError):
                 return Response({
                    "success": False,
                    "message": "Invalid category ID format"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response({
                        "success": True,
                        "data": serializer.data
                    }, status=status.HTTP_200_OK)
                except Exception as save_err:
                     return Response({
                        "success": False,
                        "message": "Failed to update category",
                        "error": str(save_err)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred during category update",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryToggleView(APIView):
    def patch(self, request, category_id):
        try:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Category not found"
                }, status=status.HTTP_404_NOT_FOUND)
            except (ValueError, TypeError):
                return Response({
                    "success": False,
                    "message": "Invalid category ID format"
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                category.status = "InActive" if category.status == "Active" else "Active"
                category.save()
                return Response({
                    "success": True,
                    "data": CategorySerializer(category).data
                }, status=status.HTTP_200_OK)
            except Exception as save_err:
                 return Response({
                    "success": False,
                    "message": f"Failed to {'deactivate' if category.status == 'Active' else 'activate'} category",
                    "error": str(save_err)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred during category status toggle",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryDeleteView(APIView):
    def delete(self, request, category_id):
        try:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Category not found"
                }, status=status.HTTP_404_NOT_FOUND)
            except (ValueError, TypeError):
                return Response({
                    "success": False,
                    "message": "Invalid category ID format"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # CASCADE manually for clarity and reporting count
                problems_qs = category.problems.all()
                count = problems_qs.count()
                problems_qs.delete()
                category.delete()
                
                return Response({
                    "success": True,
                    "message": f"Category and {count} associated problems deleted successfully"
                }, status=status.HTTP_200_OK)
            except Exception as del_err:
                 return Response({
                    "success": False,
                    "message": "Failed to delete category and its problems",
                    "error": str(del_err)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred during category deletion",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
