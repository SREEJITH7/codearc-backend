

from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings


from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

class LogoutView(APIView):
    def post(self, request):
        role = request.data.get("role", "user")
        logger.info(f"Logout sequence initiated for role: {role}")
        
        response = Response(
            {"success": True, "message": "Logged out Successfully"}
        )

        # Determine cookie names based on role
        if role == "admin":
            access_cookie = settings.ADMIN_ACCESS_COOKIE
            refresh_cookie = settings.ADMIN_REFRESH_COOKIE
        elif role == "recruiter":
            access_cookie = settings.RECRUITER_ACCESS_COOKIE
            refresh_cookie = settings.RECRUITER_REFRESH_COOKIE
        else:
            access_cookie = settings.USER_ACCESS_COOKIE
            refresh_cookie = settings.USER_REFRESH_COOKIE

        try:
            refresh_token = request.COOKIES.get(refresh_cookie)
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.info(f"Refresh token for {role} blacklisted successfully")
            else:
                logger.warning(f"Logout attempted but {role} refresh token cookie was missing")
        except Exception as e:
            logger.error(f"Error blacklisting token during logout: {str(e)}")

        response.delete_cookie(access_cookie, path="/")
        response.delete_cookie(refresh_cookie, path="/")

        return response


