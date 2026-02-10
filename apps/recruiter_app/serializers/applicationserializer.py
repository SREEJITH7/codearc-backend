from rest_framework import serializers
from apps.recruiter_app.models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            'id',
            'job',
            'user',
            'name',
            'email',
            'contactNo',
            'location',
            'education',
            'workExperience',
            'links',
            'aboutYourself',
            'skills',
            'resume',
            'plusTwoCertificate',
            'degreeCertificate',
            'pgCertificate',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']

    def validate_education(self, value):
        """Validate education JSON structure"""
        required_fields = ['highestQualification', 'qualificationName', 
                          'institutionName', 'yearOfGraduation', 'cgpa']
        
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(
                    f"Education must contain '{field}' field"
                )
        
        return value

    def validate_skills(self, value):
        """Validate skills is a list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Skills must be a list")
        
        if len(value) == 0:
            raise serializers.ValidationError("At least one skill is required")
        
        return value
