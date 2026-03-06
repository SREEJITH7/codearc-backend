from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user_id = access_token["user_id"]
        return User.objects.get(id=user_id)
    except Exception as e:
        import traceback
        print(f"JWT AUTH ERROR: {str(e)}")
        traceback.print_exc()
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from django.conf import settings
        
        token = None
        
        # 1. Try Query String
        query_string = parse_qs(scope["query_string"].decode())
        if "token" in query_string:
            token = query_string["token"][0]
            
        # 2. Try Cookies from Headers (Handles HttpOnly)
        if not token:
            headers = dict(scope.get("headers", []))
            if b"cookie" in headers:
                cookies_str = headers[b"cookie"].decode()
                cookies = {}
                for item in cookies_str.split(";"):
                    if "=" in item:
                        k, v = item.split("=", 1)
                        cookies[k.strip()] = v.strip()
                
                possible_cookies = [
                    getattr(settings, "ADMIN_ACCESS_COOKIE", "admin_access_token"),
                    getattr(settings, "RECRUITER_ACCESS_COOKIE", "recruiter_access_token"),
                    getattr(settings, "USER_ACCESS_COOKIE", "user_access_token"),
                    "access_token"
                ]
                
                for cookie_name in possible_cookies:
                    if cookie_name in cookies:
                        token = cookies[cookie_name]
                        break

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)