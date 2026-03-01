from rest_framework import serializers
from ..models import Job, Application
import json


class JobSerializer(serializers.ModelSerializer):
    _id = serializers.ReadOnlyField(source='id')
    recruiter = serializers.ReadOnlyField(source='recruiter.id')

    jobrole = serializers.CharField(source='title', required=False)
    jobLocation = serializers.CharField(source='location', required=False)
    workMode = serializers.SerializerMethodField()
    workTime = serializers.SerializerMethodField()
    minExperience = serializers.IntegerField(source='experience', required=False)

    requirements = serializers.JSONField(source='skills', required=False)
    responsibilities = serializers.JSONField(required=False)

    minSalary = serializers.IntegerField(source='min_salary', required=False)
    maxSalary = serializers.IntegerField(source='max_salary', required=False)

    status = serializers.SerializerMethodField()
    isApplied = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            '_id', 'id', 'recruiter', 'title', 'jobrole', 'location', 'jobLocation',
            'workMode', 'workTime', 'job_type', 'experience', 'minExperience',
            'requirements', 'responsibilities',
            'minSalary', 'maxSalary',
            'status', 'created_at', 'description', 'skills', 'isApplied'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def get_workMode(self, obj):
        return obj.job_type

    def get_workTime(self, obj):
        return obj.work_time


    def get_status(self, obj):
        return 'Active' if obj.status == 'OPEN' else 'Inactive'

    def get_isApplied(self, obj):
        if hasattr(obj, 'isApplied'):
            return obj.isApplied
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return Application.objects.filter(job=obj, user=request.user).exists()
        return False

    def to_internal_value(self, data):
        # DRF handles 'source' mapping automatically in super().to_internal_value
        # for fields like minSalary -> min_salary. 
        # Manual popping here was causing fields to be missing when super() was called,
        # leading to default values (0) being used.

        if 'workMode' in data and 'job_type' not in data:
            mode_mapping = {
                'remote':  'REMOTE',
                'on-site': 'ONSITE',
                'hybrid':  'HYBRID',
            }
            work_mode = data.get('workMode', '').lower()
            data['job_type'] = mode_mapping.get(work_mode, 'REMOTE')

        return super().to_internal_value(data)