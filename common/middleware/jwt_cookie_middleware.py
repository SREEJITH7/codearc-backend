from django.conf import settings
import re

class JwtCookieToHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_patterns = [
            re.compile(r'^/api/auth/signup/'),
            re.compile(r'^/api/auth/login/'),
            re.compile(r'^/api/auth/recruiter/login$'),
            re.compile(r'^/api/auth/google/'),
            re.compile(r'^/api/auth/verify-otp/'),
            re.compile(r'^/api/auth/resend-otp/'),
            re.compile(r'^/api/auth/forgot-password/'),
            re.compile(r'^/api/auth/reset-password/'),
            re.compile(r'^/api/auth/refresh-token/'),
            re.compile(r'^/admin/'),
        ]

    def __call__(self, request):
        # 1. Handle Preflight OPTIONS manually to bypass cached '*' wildcard issues
        if request.method == "OPTIONS":
            from django.http import HttpResponse
            response = HttpResponse(status=200)
            
            # Use the actual origin from the request if it's in our allowed list
            origin = request.headers.get("Origin")
            allowed_origins = [
                "http://localhost:5173", "http://127.0.0.1:5173",
                "http://localhost:5174", "http://127.0.0.1:5174"
            ]
            
            if origin in allowed_origins:
                response["Access-Control-Allow-Origin"] = origin
            else:
                response["Access-Control-Allow-Origin"] = "http://localhost:5173" # Default
            
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-CSRFToken, accept, origin, dnt, user-agent"
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Max-Age"] = "0" # Do not cache these preflights
            return response

        is_public = any(pattern.match(request.path) for pattern in self.public_patterns)

        if not is_public:
            path = request.path
            access_token = None

            if path.startswith(('/api/admin/', '/admin/')):
                access_token = request.COOKIES.get(settings.ADMIN_ACCESS_COOKIE)
            elif path.startswith('/api/recruiter/'):
                access_token = request.COOKIES.get(settings.RECRUITER_ACCESS_COOKIE)
            else:
                access_token = (
                    request.COOKIES.get(settings.USER_ACCESS_COOKIE) or
                    request.COOKIES.get(settings.RECRUITER_ACCESS_COOKIE) or
                    request.COOKIES.get(settings.ADMIN_ACCESS_COOKIE)
                )

            if access_token:
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

        response = self.get_response(request)

        if "access_token" in request.COOKIES:
            response.delete_cookie("access_token")
        if "refresh_token" in request.COOKIES:
            response.delete_cookie("refresh_token")

        return response