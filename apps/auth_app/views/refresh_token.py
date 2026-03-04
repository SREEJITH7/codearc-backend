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
        role = request.data.get("role", "user")
        
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

        # 1. Get refresh token from cookie
        refresh_token = request.COOKIES.get(refresh_cookie)
        
        if not refresh_token:
            logger.warning(f"Token Refresh: {role} Refresh token missing from cookies")
            return Response(
                {"success": False, "message": "Refresh token not found"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. Use serializer explicitly (This handles blacklisting internally)
        serializer = self.get_serializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError) as e:
            logger.error(f"Token Refresh Failed for {role}: {str(e)}")
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
            key=access_cookie,
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
                key=refresh_cookie,
                value=new_refresh_token,
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
                max_age=60 * 60 * 24 * 7,
                path="/",
            )
            logger.info(f"Access and Refresh tokens rotated successfully for {role}")
        else:
            logger.info(f"Access token renewed successfully for {role}")

        return response
