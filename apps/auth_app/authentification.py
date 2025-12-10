# apps/auth_app/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    Read JWT access token from cookies['access'] if Authorization header absent.
    Inherits rest_framework_simplejwt.authentication.JWTAuthentication behaviors.
    """
    def get_header(self, request):
        # try original header

        header = super().get_header(request)
        if header:
            return header
        # If no Authorization header, attempt to read from cookie

        raw_token = request.COOKIES.get('access')
        if raw_token is None:
            return None
        
        # Return a header-like bytes object expected by parent class
        return f"Bearer {raw_token}".encode('utf-8')
