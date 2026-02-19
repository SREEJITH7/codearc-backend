from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..models import Job
from ..serializers.jobserializer import JobSerializer
from ..permissions import Isrecruiter


class RecruiterJobViewSet(ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, Isrecruiter]

    def get_queryset(self):
        return Job.objects.filter(recruiter=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        
        status_filter = request.query_params.get('status', None)
        if status_filter:
            status_mapping = {
                'active': 'OPEN',
                'blocked': 'CLOSED',
                'inactive': 'CLOSED'
            }
            backend_status = status_mapping.get(status_filter.lower(), None)
            if backend_status:
                queryset = queryset.filter(status=backend_status)
        
        
        workmode_filter = request.query_params.get('workmode', None)
        if workmode_filter:
            queryset = queryset.filter(job_type=workmode_filter)
             

        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 6))
        
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        
        paginated_queryset = queryset[start:end]
        serializer = self.get_serializer(paginated_queryset, many=True)
        
        return Response({
            'success': True,
            'data': {
                'jobs': serializer.data,
                'pagination': {
                    'total': total,
                    'page': page,
                    'pages': (total + limit - 1) // limit,  
                    'limit': limit,
                    'hasNextPage': end < total,
                    'hasPrevPage': page > 1
                }
            }
        })
    
    @action(detail=True, methods=['patch'], url_path='toggle_status')
    def toggle_status(self, request, pk=None):
        job = self.get_object()
        if job.status == 'OPEN':
            job.status = 'CLOSED'
        else:
            job.status = 'OPEN'
        
        job.save()
        
         
        serializer = self.get_serializer(job)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='locations')
    def proxy_locations(self, request):
         
        # Proxy location search to Nominatim API
        
        query = request.query_params.get('q')
        if not query:
            return Response({'success': False, 'data': []})

        try:
            import requests
            headers = {
                'User-Agent': 'CodeArc Application'
            }
            url = (
            f"https://nominatim.openstreetmap.org/search"
            f"?format=json"
            f"&q={query}"
            f"&countrycodes=in"
            f"&addressdetails=1"
            f"&limit=5"
        )
            response = requests.get(url, headers=headers, timeout=5)
            data = response.json()
            return Response({'success': True, 'data': data})
        except Exception as e:
            return Response({'success': False, 'data': [], 'message': str(e)}, status=500)
