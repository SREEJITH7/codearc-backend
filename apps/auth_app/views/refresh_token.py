from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # 1. Get refresh token from cookie
        refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        
        if not refresh_token:
            logger.warning("Token Refresh: Refresh token missing from cookies")
            return Response(
                {"success": False, "message": "Refresh token not found"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. Use serializer explicitly (This handles blacklisting internally)
        serializer = self.get_serializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError) as e:
            logger.error(f"Token Refresh Failed: {str(e)}")
            return Response(
                {"success": False, "message": str(e)}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 3. Successful refresh
        access_token = serializer.validated_data.get("access")
        new_refresh_token = serializer.validated_data.get("refresh")

        response = Response({
            "success": True, 
            "message": "Token refreshed successfully"
        }, status=status.HTTP_200_OK)

        # 4. Set access token cookie
        response.set_cookie(
            key=settings.ACCESS_COOKIE_NAME,
            value=access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=60 * 15,
            path="/",
        )

        # 5. Set new refresh token cookie if rotation is enabled
        if new_refresh_token:
            response.set_cookie(
                key=settings.REFRESH_COOKIE_NAME,
                value=new_refresh_token,
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
                max_age=60 * 60 * 24 * 7,
                path="/",
            )
            logger.info("Access and Refresh tokens rotated successfully")
        else:
            logger.info("Access token renewed successfully")

        return response
