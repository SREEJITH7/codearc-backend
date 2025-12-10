# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import AuthenticationFailed

# class JWTAuthMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.jwt_auth = JWTAuthentication()

#     def __call__(self, request):
#         try:
#             user_auth_tuple = self.jwt_auth.authenticate(request)
#             if user_auth_tuple is not None:
#                 request.user, _ = user_auth_tuple
#         except AuthenticationFailed:
#             pass  # allow unauthenticated access for public endpoints
#         return self.get_response(request)
# common/middleware/jwt_cookie_middleware.py




# from django.utils.deprecation import MiddlewareMixin

# class JwtCookieToHeaderMiddleware(MiddlewareMixin):
#     """
#     If an 'access' cookie exists, add Authorization header for DRF SimpleJWT to read.
#     Keeps existing behavior otherwise.
#     Place this **before** AuthenticationMiddleware in MIDDLEWARE list (or early).
#     """
#     def process_request(self, request):
#         access = request.COOKIES.get("access")
#         # Only set header if not already present
#         if access and "HTTP_AUTHORIZATION" not in request.META:
#             request.META["HTTP_AUTHORIZATION"] = f"Bearer {access}"
#         return None


# common/middleware/jwt_cookie_middleware.py
# --------------------------------------------------------
# from django.conf import settings

# class JwtCookieToHeaderMiddleware:
#     """
#     If JWT tokens are present in cookies, move the access token
#     into Authorization header so DRF SimpleJWT can authenticate normally.
#     """
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.access_cookie = getattr(settings, "ACCESS_COOKIE_NAME", "access")

#     def __call__(self, request):
#         # If header not set but cookie exists -> set header for downstream auth
#         if "HTTP_AUTHORIZATION" not in request.META:
#             token = request.COOKIES.get(self.access_cookie)
#             if token:
#                 request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"
#         return self.get_response(request)
    

    # -------------------

# class JwtCookieToHeaderMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):

#         # IMPORTANT: Skip CORS preflight requests
#         if request.method == "OPTIONS":
#             return self.get_response(request)

#         # Only inject header for actual browser requests
#         access = request.COOKIES.get("access")
#         if access:
#             request.META["HTTP_AUTHORIZATION"] = f"Bearer {access}"

#         return self.get_response(request)

# common/middleware/jwt_cookie_middleware.py
# ---------------------------------------------------------------------------------------------
# class JwtCookieToHeaderMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Skip preflight
#         if request.method == "OPTIONS":
#             return self.get_response(request)

#         # ←←← CORRECT NAME
#         access = request.COOKIES.get("access_token")   # was "access"
#         if access:
#             request.META["HTTP_AUTHORIZATION"] = f"Bearer {access}"

#         return self.get_response(request)

# ----------------------------------------------------------------------------
# import re

# class JwtCookieToHeaderMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # Compile regex patterns for better performance
#         self.public_patterns = [
#             re.compile(r'^/api/auth/'),  # All auth endpoints
#             re.compile(r'^/api/public/'),  # Any public API
#         ]

#     def __call__(self, request):
#         # Skip preflight
#         if request.method == "OPTIONS":
#             return self.get_response(request)

#         # ✅ Skip JWT injection for public endpoints
#         is_public = any(pattern.match(request.path) for pattern in self.public_patterns)
        
#         if is_public:
#             return self.get_response(request)

#         # Extract access token from cookie and add to header
#         access = request.COOKIES.get("access_token")
#         if access:
#             request.META["HTTP_AUTHORIZATION"] = f"Bearer {access}"

#         return self.get_response(request)


# common/middleware/jwt_cookie_middleware.py

# common/middleware/jwt_cookie_middleware.py

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
    re.compile(r'^/api/auth/refresh-token/'),  # 🔥 MUST ADD
    re.compile(r'^/admin/'),
]


    def __call__(self, request):
        # Skip preflight
        if request.method == "OPTIONS":
            return self.get_response(request)

        # Check if this is a public endpoint
        is_public = any(pattern.match(request.path) for pattern in self.public_patterns)
        
        if not is_public:
            # Extract access token from cookie
            access_token = request.COOKIES.get("access_token")
            
            print(f"🔍 Path: {request.path}")
            print(f"🔍 Is Public: {is_public}")
            print(f"🍪 Access Token Present: {'Yes' if access_token else 'No'}")
            
            if access_token:
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
                print(f"✅ JWT injected for: {request.path}")
            else:
                print(f"⚠️ No access token cookie found!")
                print(f"Available cookies: {list(request.COOKIES.keys())}")

        return self.get_response(request)