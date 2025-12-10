# auth_app/serializers/verify_otp_serializer.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.auth_app.services.otp_service import OTPService
from apps.auth_app.models import UserProfile, RecruiterProfile

User = get_user_model()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    purpose = serializers.CharField(default="REGISTRATION")

    def validate(self, data):
        ok, msg = OTPService.verify_otp(data["email"], data["otp"], data["purpose"])
        if not ok:
            raise serializers.ValidationError(msg)
        return data

    def create(self, validated_data):
        user = User.objects.get(email=validated_data["email"])
        user.is_verified = True
        user.save()

        if user.role == "user":
            UserProfile.objects.get_or_create(user=user)
        elif user.role == "recruiter":
            RecruiterProfile.objects.get_or_create(user=user)

        OTPService.delete_otp(validated_data["email"])
        return user
