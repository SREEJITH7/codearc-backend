# auth_app/services/auth_service.py

from django.contrib.auth import get_user_model
from django.db import transaction
from apps.auth_app.services.otp_service import OTPService
from apps.auth_app.services.email_service import send_otp_email

User = get_user_model()

class AuthService:

    @staticmethod
    def email_exists(email: str):
        return User.objects.filter(email=email).exists()

    @staticmethod
    @transaction.atomic
    def create_user_and_send_otp(email, username, password, role="user"):
        if AuthService.email_exists(email):
            return None, "Email already registered"

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            role=role,
            is_active=True,
            is_verified=False
        )

        # generate_and_send_otp already saves the OTP to cache and sends the email
        OTPService.generate_and_send_otp(email, purpose="REGISTRATION")

        return user, "OTP sent"
