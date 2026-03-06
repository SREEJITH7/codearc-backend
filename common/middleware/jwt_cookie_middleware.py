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
        # OPTIONS preflight is handled entirely by CorsMiddleware (runs before this middleware).
        # Do NOT intercept OPTIONS here — returning a new HttpResponse would replace the
        # carefully set Access-Control-Allow-Origin header that CorsMiddleware already added.
        if request.method == "OPTIONS":
            return self.get_response(request)

        is_public = any(pattern.match(request.path) for pattern in self.public_patterns)

        if not is_public:
            # ONLY move cookie to header if Authorization header is NOT already set by frontend
            if "HTTP_AUTHORIZATION" in request.META:
                return self.get_response(request)

            path = request.path
            access_token = None

            if path.startswith(('/api/admin/', '/admin/')):
                access_token = request.COOKIES.get(settings.ADMIN_ACCESS_COOKIE)
            elif path.startswith('/api/recruiter/'):
                access_token = request.COOKIES.get(settings.RECRUITER_ACCESS_COOKIE)
            else:
                # Prioritize Admin > Recruiter > User for generic paths like /api/chat/
                access_token = (
                    request.COOKIES.get(settings.ADMIN_ACCESS_COOKIE) or
                    request.COOKIES.get(settings.RECRUITER_ACCESS_COOKIE) or
                    request.COOKIES.get(settings.USER_ACCESS_COOKIE)
                )

            if access_token:
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

        response = self.get_response(request)

        if "access_token" in request.COOKIES:
            response.delete_cookie("access_token")
        if "refresh_token" in request.COOKIES:
            response.delete_cookie("refresh_token")

        return response