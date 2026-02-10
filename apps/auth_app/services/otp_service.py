# auth_app/services/otp_service.py

from django.core.cache import cache
from datetime import timedelta
from apps.auth_app.models import OTP
# from common.email_service import send_email 
from apps.auth_app.services.email_service import send_otp_email


class OTPService:

    OTP_TTL = 300  # 5 minutes

    @staticmethod
    def generate_and_send_otp(email, purpose="REGISTRATION"):
        otp = OTP.generate_otp()

        print(f"[OTP DEBUG] Email: {email}, Purpose: {purpose}, OTP: {otp}")

        # Save OTP in Redis
        key = f"otp:{purpose}:{email}"
        cache.set(key, otp, timeout=OTPService.OTP_TTL)
 
        send_otp_email(email, otp)

        return True, "OTP sent"

    @staticmethod
    def save_otp(email: str, otp: str, purpose="REGISTRATION"):
        key = f"otp:{purpose}:{email}"
        cache.set(key, otp, timeout=OTPService.OTP_TTL)
        return True

    @staticmethod
    def verify_otp(email: str, otp: str, purpose="REGISTRATION"):
        key = f"otp:{purpose}:{email}"
        stored_otp = cache.get(key)

        if not stored_otp:
            return False, "OTP expired or not found"

        if stored_otp != otp:
            return False, "Invalid OTP"

        return True, "OTP verified"

    @staticmethod
    def delete_otp(email: str, purpose="REGISTRATION"):
        key = f"otp:{purpose}:{email}"
        cache.delete(key)


# --------------------------------
 