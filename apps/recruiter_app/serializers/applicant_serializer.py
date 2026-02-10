from rest_framework import serializers
from apps.recruiter_app.models import Application

class RecruiterApllicantListSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only = True)
    applicant_name = serializers.CharField(source="name", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "applicant_name",
            "email",
            "contactNo",
            "job_title",
            "status",
            "created_at",
        ]


class RecruiterApplicantDetailSerializer(serializers.ModelSerializer):
    job = serializers.StringRelatedField()

    class Meta:
        model = Application
        exclude = []

        
