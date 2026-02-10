from rest_framework import serializers
from ..models import Job, Application
import json


class JobSerializer(serializers.ModelSerializer):
    _id = serializers.ReadOnlyField(source='id')
    recruiter = serializers.ReadOnlyField(source='recruiter.id')
    
     
    jobrole = serializers.CharField(source='title', required=False)
    jobLocation = serializers.CharField(source='location', required=False)
    workMode = serializers.SerializerMethodField(required=False)
    workTime = serializers.SerializerMethodField(required=False)
    minExperience = serializers.IntegerField(source='experience', required=False)

    requirements = serializers.SerializerMethodField()
    responsibilities = serializers.JSONField(required=False)

    minSalary = serializers.IntegerField(source='min_salary', required=False)
    maxSalary = serializers.IntegerField(source='max_salary', required=False)
    
    status = serializers.SerializerMethodField()
    
    isApplied = serializers.SerializerMethodField()
    class Meta:
        model = Job
        fields = [
            '_id', 'id', 'recruiter', 'title', 'jobrole', 'location', 'jobLocation', 'workMode', 
            'workTime', 'job_type', 'experience', 'minExperience', 'requirements', 'responsibilities',
            'minSalary', 'maxSalary', 'status', 'created_at', 'description', 'skills', 'isApplied'
        ]
        extra_kwargs = {
            '_id': {'source': 'id', 'read_only': True},
            'id': {'read_only': True}
        }
    
    def get_workMode(self, obj):
        mapping = {
            'REMOTE': 'remote',
            'ONSITE': 'on-site',
            'HYBRID': 'hybrid'
        }
        return mapping.get(obj.job_type, 'remote')
    
    def get_workTime(self, obj):
        
        return 'full-time'
    
    def get_requirements(self, obj):
        
        if isinstance(obj.skills, list):
            return obj.skills
        elif isinstance(obj.skills, str):
            try:
                return json.loads(obj.skills)
            except:
                return []
        return []
    
    def get_responsibilities(self, obj):
        
        return obj.responsibilities or []
    
    def get_minSalary(self, obj):
        
        return obj.min_salary
    
    def get_maxSalary(self, obj):
        
        return obj.max_salary
    
    def get_status(self, obj):
        return 'Active' if obj.status == 'OPEN' else 'Inactive'
    
    def get_isApplied(self, obj):
        if hasattr(obj, 'isApplied'):
            return obj.isApplied

        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return Application.objects.filter(
                job=obj,
                user=request.user
            ).exists()

        return False


    def to_internal_value(self, data):
         
        # Handle aliased fields if present
        if 'jobrole' in data and 'title' not in data:
            data['title'] = data.pop('jobrole')
        if 'jobLocation' in data and 'location' not in data:
            data['location'] = data.pop('jobLocation')
        if 'workMode' in data and 'job_type' not in data:
            mode_mapping = {
                'remote': 'REMOTE',
                'on-site': 'ONSITE',
                'hybrid': 'HYBRID'
            }
            data['job_type'] = mode_mapping.get(data.pop('workMode'), 'REMOTE')
        if 'minExperience' in data and 'experience' not in data:
            data['experience'] = data.pop('minExperience')
        
        if 'minSalary' in data and 'min_salary' not in data:
            data['min_salary'] = data.pop('minSalary')
        if 'maxSalary' in data and 'max_salary' not in data:
            data['max_salary'] = data.pop('maxSalary')
        if 'workTime' in data and 'work_time' not in data:
            data['work_time'] = data.pop('workTime')
            
        if 'requirements' in data and 'skills' not in data:
            data['skills'] = data.pop('requirements')
        
        return super().to_internal_value(data)
