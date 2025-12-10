# auth_app/services/email_service.py

from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email ,otp ):

    subject = "Your OTP Code"
    message = f"Your OTP code is {otp}. It expires in 5 minutes."


    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )

    return True


