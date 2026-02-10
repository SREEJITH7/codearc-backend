# apps/auth_app/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):

    def get_header(self, request):
        
        header = super().get_header(request)
        if header:
            return header
         
        raw_token = request.COOKIES.get('access')
        if raw_token is None:
            return None
        
        return f"Bearer {raw_token}".encode('utf-8')
