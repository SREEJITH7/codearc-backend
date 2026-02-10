from rest_framework import serializers
from apps.auth_app.models import RecruiterProfile


class RecruiterProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source= "user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only= True)

    class Meta:
        model = RecruiterProfile
        fields = [
           "id",

            
            "username",
            "email",

            
            "contact_person",
            "phone",
            "company_name",
            "company_type",
            "year_established",
            "registration_certificate",
            "profileimage",
            "location",

            
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
            "username",
            "email",
        ]