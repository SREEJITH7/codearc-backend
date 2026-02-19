from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.recruiter_app.models import Job, Application
from apps.recruiter_app.serializers.jobserializer import JobSerializer
from apps.recruiter_app.serializers.applicationserializer import ApplicationSerializer
import json
from django.db.models import Exists, OuterRef , Q, Value, BooleanField


class UserJobListView(APIView):
    """
    View for users to browse all active job postings
    Includes pagination, search, and filters
    """
    permission_classes = []  # Public access or authenticated users

    def get(self, request):
        try:
            queryset = Job.objects.filter(status='OPEN').order_by('-created_at')
            user = request.user if request.user.is_authenticated else None

            if user:
                queryset = queryset.annotate(
                isApplied=Exists(
                Application.objects.filter(
                    job=OuterRef('pk'),
                    user=user
                )
            )
        )
            else:
                queryset = queryset.annotate(
                isApplied=Value(False, output_field=BooleanField())
        )

            
            search = request.query_params.get('search', None)
            if search:
                queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
            
            
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
                workmode_mapping = {
                    'remote': 'REMOTE',
                    'on-site': 'ONSITE',
                    'hybrid': 'HYBRID'
                }
                backend_workmode = workmode_mapping.get(workmode_filter.lower(), None)
                if backend_workmode:
                    queryset = queryset.filter(job_type=backend_workmode)
            
            
            worktime_filter = request.query_params.get('worktime', None)
            if worktime_filter:
                queryset = queryset.filter(work_time__iexact=worktime_filter)

            # Location filter
            location_filter = request.query_params.get('location', None)
            if location_filter:
                queryset = queryset.filter(location__icontains=location_filter)

            # Skills filter
            skills_filter = request.query_params.get('skills', None)
            if skills_filter:
                skills_list = [s.strip() for s in skills_filter.split(',') if s.strip()]
                for skill in skills_list:
                    queryset = queryset.filter(skills__icontains=skill)
            
            try:
                page = int(request.query_params.get('page', 1))
                limit = int(request.query_params.get('limit', 6))
            except (ValueError, TypeError):
                page = 1
                limit = 6
            
            total = queryset.count()
            start = (page - 1) * limit
            end = start + limit
            
            paginated_queryset = queryset[start:end]
            serializer = JobSerializer(paginated_queryset, many=True, context={'request': request})
            

            return Response({
                'success': True,
                'data': {
                    'jobs': serializer.data,
                    'pagination': {
                        'total': total,
                        'page': page,
                        'pages': (total + limit - 1) // limit if limit > 0 else 1,   
                        'limit': limit,
                        'hasNextPage': end < total,
                        'hasPrevPage': page > 1
                    }
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while fetching jobs',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SingleJobView(APIView):
    """
    View to get a single job by ID
    """
    permission_classes = []   

    def get(self, request, job_id):
        try:
            # Allow fetching the job even if it is CLOSED (so candidates see the 'closed' message)
            job = Job.objects.get(id=job_id)
            serializer = JobSerializer(job, context={'request': request})
            
            return Response({
                'success': True,
                'data': serializer.data
            })
        
        except Job.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Job not found'
            }, status=status.HTTP_404_NOT_FOUND)


class JobApplicationView(APIView):
    """
    View to handle job application submissions
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
             
            data = request.data.dict() if hasattr(request.data, 'dict') else request.data.copy()
            
             
            json_fields = ['education', 'workExperience', 'links', 'skills']
            for field in json_fields:
                val = data.get(field)
                if val and isinstance(val, str):
                    try:
                        data[field] = json.loads(val)
                    except json.JSONDecodeError:
                        return Response({
                            'success': False,
                            'message': f'Invalid JSON format for {field}'
                        }, status=status.HTTP_400_BAD_REQUEST)

             
            data['user'] = request.user.id

             
            job_id = data.get('jobId') or data.get('job')
            if not job_id:
                return Response({
                    'success': False,
                    'message': 'Job ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                job = Job.objects.get(id=job_id) 
                
                if job.status == 'CLOSED':
                    return Response({
                        "success": False,
                        "message": "This position is no longer accepting applications"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                data['job'] = job.id
            except (Job.DoesNotExist, ValueError):
                return Response({
                    "success": False,
                    "message": "Job not found"
                }, status=status.HTTP_404_NOT_FOUND)

            # Check if user already applied
            if Application.objects.filter(job=job, user=request.user).exists():
                return Response({
                    'success': False,
                    'message': 'You have already applied to this job'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create the application
            serializer = ApplicationSerializer(data=data)
            
            if serializer.is_valid():
                serializer.save()
                
                return Response({
                    'success': True,
                    'message': 'Application submitted successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
