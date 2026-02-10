from rest_framework.generics import ListAPIView
from ..models import Job
from ..serializers import jobserializer


class PublicJobListView(ListAPIView):
    serializer_class = jobserializer.JobSerializer
    permission_classes = []

    def get_queryset(self):
        return Job.objects.filter(status='OPEN').order_by('-created_at')


    
