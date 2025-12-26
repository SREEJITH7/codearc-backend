
# auth_app/serializers/signup_serializer.py

from rest_framework import serializers
from apps.auth_app.services.auth_service import AuthService
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'role']
        read_only_fields = ['id']  # UUID is auto-generated

    def validate_email(self, value):
        if AuthService.email_exists(value):
            raise serializers.ValidationError("Email already registered")
        return value

    def create(self, validated_data):
        user, message = AuthService.create_user_and_send_otp(
            validated_data["email"],
            validated_data["username"],
            validated_data["password"],
            validated_data["role"],
        )
        return user



