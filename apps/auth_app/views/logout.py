

from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings


from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

class LogoutView(APIView):
    def post(self, request):
        logger.info("Logout sequence initiated")
        
        response = Response(
            {"success": True, "message": "Logged out Successfully"}
        )

        try:
            refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.info("Refresh token blacklisted successfully")
            else:
                logger.warning("Logout attempted but refresh token cookie was missing")
        except Exception as e:
            logger.error(f"Error blacklisting token during logout: {str(e)}")
            # Even if blacklisting fails (e.g., token already invalid), 
            # we continue to clear cookies for the user experience

        response.delete_cookie(settings.ACCESS_COOKIE_NAME, path="/")
        response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/")

        return response


