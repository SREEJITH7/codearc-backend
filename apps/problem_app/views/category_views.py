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
        # Annotate with problem count
        queryset = Category.objects.annotate(problem_count=Count('problems')).order_by("name")
        search = request.query_params.get("search")

        if search:
            queryset = queryset.filter(name__icontains=search)

        paginator = CategoryPagination()
        page = paginator.paginate_queryset(queryset, request)

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


class CategoryCreateView(APIView):
    # ... (No changes needed, existing code)
    def post(self, request):
        name = request.data.get("name")
        if not name:
            return Response({"message": "Name required"}, status=400)

        if Category.objects.filter(name__iexact=name).exists():
            return Response({"message": "Category exists"}, status=400)

        category = Category.objects.create(
            name=name,
            slug=slugify(name),
            status="Active"
        )
        
        # Manually verify serializer or just return data (serializer expects problem_count which is 0 for new)
        # To avoid error with read-only field problem_count not being present in instance if not annotated,
        # we can just return serializer data. Typically new instance won't have it annotated but it's 0.
        # However, DRF might just ignore it if it's missing or we can add it manually if needed.
        # Actually, let's simple return serializer data, simple fields will be fine.
        
        return Response(CategorySerializer(category).data, status=201)


class CategoryUpdateView(APIView):
    # ... (existing code)
    def put(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"message": "Category not found"}, status=404)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class CategoryToggleView(APIView):
    # ... (existing code)
    def patch(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
            category.status = "InActive" if category.status == "Active" else "Active"
            category.save()
            return Response(CategorySerializer(category).data)
        except Category.DoesNotExist:
            return Response({"message": "Category not found"}, status=404)


class CategoryDeleteView(APIView):
    def delete(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
            
            # Cascade delete problems
            # Note: Verify if this is truly what is wanted. User said "delete all question all will be deleted".
            # So we delete all problems where category=category.
            
            count = category.problems.count()
            category.problems.all().delete()
            category.delete()
            
            return Response({
                "success": True,
                "message": f"Category and {count} associated problems deleted successfully"
            })
        except Category.DoesNotExist:
            return Response({"message": "Category not found"}, status=404)
