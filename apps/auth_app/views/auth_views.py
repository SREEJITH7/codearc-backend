# auth_app/views/auth_views.py

import uuid
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.auth_app.serializers.signup_serializer import SignupSerializer
from apps.auth_app.serializers.verify_otp_serializer import VerifyOTPSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
from apps.auth_app.services.otp_service import OTPService
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
# from .models import User, UserProfile
from apps.auth_app.models import User ,UserProfile
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse
import requests
import json
from urllib.parse import urlencode
# from apps.auth_app.models import User,UserProfile
import json
from django.core.cache import cache
from urllib.parse import quote, unquote

# need to move the seperate admin app later
from django.core.paginator import Paginator
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
User = get_user_model()
 
import logging

logger = logging.getLogger(__name__)

class SignupView(APIView):
    def post(self, request):
        email = request.data.get("email").lower().strip()  
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                return Response(
                    {"email": ["User with this email already exists."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            OTPService.delete_otp(email, purpose="REGISTRATION")  
            ok, msg = OTPService.generate_and_send_otp(email, purpose="REGISTRATION")
            if ok:
                return Response({"message": "OTP resent", "email": email}, status=200)
            return Response({"message": msg}, status=400)

        except User.DoesNotExist:
            serializer = SignupSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()   
                OTPService.delete_otp(email, purpose="REGISTRATION")   
                ok, msg = OTPService.generate_and_send_otp(email, purpose="REGISTRATION")
                if not ok:
                    return Response(
                        {"message": "Account created but failed to send OTP. Please resend."},
                        status=201
                    )
                return Response(
                    {"message": "OTP sent successfully", "email": email},
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Account verified"}, status=status.HTTP_200_OK)
        print("OTP VERIFY ERRORS:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"message": "Email required"}, status=400)

        # delete old OTP
        OTPService.delete_otp(email)

        # create new and send
        ok, msg = OTPService.generate_and_send_otp(email)

        if ok:
            return Response({"message": "OTP resent successfully"}, status=200)
        else:
            return Response({"message": msg}, status=400)



    

class LoginView(APIView):
    def post(self, request):
        logger.info(f"Login attempt from IP {request.META.get('REMOTE_ADDR')}")

        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, username=email, password=password)
        
        if user is None:
            logger.warning(f"Invalid login credentials for {email}")
            return Response({"success": False, "message": "Invalid email or password"}, status=401)
        
        if user.role != "user":
            logger.warning(f"Non-user role {user.role} tried user login: {email}")
            return Response({"success": False, "message": "This is not a user account"}, status=403)

        if not user.is_verified:
            logger.warning(f"Unverified user login attempt: {email}")
            return Response({"success": False, "message": "Please verify your email first"}, status=403)
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        response = Response({
            "success": True,
            "message": "Login successful",
            "user": {"id": user.id, "email": user.email, "role": user.role},
        }, status=200)
        
        response.set_cookie(key=settings.ACCESS_COOKIE_NAME, value=access_token,
                            httponly=True, secure=settings.COOKIE_SECURE,
                            samesite=settings.COOKIE_SAMESITE, max_age=60*15, path="/")
        
        response.set_cookie(key=settings.REFRESH_COOKIE_NAME, value=refresh_token,
                            httponly=True, secure=settings.COOKIE_SECURE,
                            samesite=settings.COOKIE_SAMESITE, max_age=60*60*24*7, path="/")
        
        logger.info(f"Successful login for user {email}")
        return response

class RecruiterLoginView(APIView):

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({"success": False, "message": "Invalid email or password"},
                            status=401)

        if user.role != "recruiter":
            return Response({"success": False, "message": "Not a recruiter account"},
                            status=403)

        if not user.is_verified:
            return Response({"success": False, "message": "Email not verified"},
                            status=403)

        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
            },
        })

        response.set_cookie(key=settings.ACCESS_COOKIE_NAME, value=access_token,
                            httponly=settings.COOKIE_HTTPONLY,
                            secure=settings.COOKIE_SECURE,
                            samesite=settings.COOKIE_SAMESITE,
                            max_age=60 * 15,
                            path="/",
                            domain="localhost",)
        

        response.set_cookie(key=settings.REFRESH_COOKIE_NAME, value=refresh_token,
                            httponly=settings.COOKIE_HTTPONLY,
                            secure=settings.COOKIE_SECURE,
                            samesite=settings.COOKIE_SAMESITE,
                            max_age=60 * 60 * 24 * 7,
                            path="/",
                            domain="localhost",)

        return response




class ForgotPasswordOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"message": "Email required"}, status=400)
        try: 
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message":"User not found"}, status=404)
        
        OTPService.delete_otp(email, purpose="RESET")

        ok, msg = OTPService.generate_and_send_otp(email, purpose="RESET")
        if ok:
            return Response({"message": "OTP sent"}, status=200)
        return Response({"message": msg}, status=400)






class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"message": "Email and password required"}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        user.set_password(password)
        user.save()

        return Response({"message": "Password reset successful"}, status=200)

 

class AdminLoginView(APIView):
    def post(self, request):
        print("\n=== ADMIN LOGIN REQUEST ===")
        print(f"Origin: {request.META.get('HTTP_ORIGIN')}")
        print(f"Data: {request.data}")
        
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"success": False, "message": "Email and password are required"}, 
                status=400
            )

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {"success": False, "message": "Invalid email or password"}, 
                status=401
            )

        if not (user.is_superuser or user.role == "admin"):
            return Response(
                {"success": False, "message": "Not an admin account"}, 
                status=403
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        print(f"\n✅ Tokens generated:")
        print(f"Access: {access_token[:50]}...")
        print(f"Refresh: {refresh_token[:50]}...")

        response = Response({
            "success": True,
            "message": "Admin login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
            }
        })

        
        response.set_cookie(
            key=settings.ACCESS_COOKIE_NAME,
            value=access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=60 * 15,
            path="/",  
        )

        response.set_cookie(
            key=settings.REFRESH_COOKIE_NAME,
            value=refresh_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=60 * 60 * 24 * 7,
            path="/",  
        )

        print(f"\n Cookies set:")
        print(f"  - {settings.ACCESS_COOKIE_NAME}")
        print(f"  - {settings.REFRESH_COOKIE_NAME}")
        print(f"Response headers: {dict(response.items())}")

        return response


from rest_framework_simplejwt.views import TokenRefreshView


class CookieTokenRefreshView(TokenRefreshView):
  
    def post(self, request, *args, **kwargs):
        print("\n" + "="*60)
        print("🔥 REFRESH TOKEN REQUEST RECEIVED")
        print("="*60)
        print(f"Origin: {request.META.get('HTTP_ORIGIN')}")
        print(f"All cookies received: {request.COOKIES}")
        print(f"refresh_token cookie: {request.COOKIES.get('refresh_token')}")
        print(f"access_token cookie: {request.COOKIES.get('access_token')}")
        print(f"Full headers: {dict(request.META)}")
        print("="*60 + "\n")

        refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        
        if not refresh_token:
            print("❌ REFRESH TOKEN MISSING → RETURNING 401")
            return Response({"detail": "Refresh token not found in cookie"}, status=401)

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found"}, 
                status=401
            )
            
        mutable_data = request.data.copy()
        mutable_data["refresh"] = refresh_token
        request._data = mutable_data                      
        
        request.data['refresh'] = refresh_token
        
         
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            response.set_cookie(
                key=settings.ACCESS_COOKIE_NAME,
                value=response.data["access"],
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
                max_age=60 * 15,
            )
       
            response.data = {"detail": "Token refreshed successfully"}
        
        return response


# -------------------------------------------------------------------







 

 

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
REDIRECT_URI = "http://localhost:8000/api/auth/google/callback/"


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Generate unique state for CSRF protection
        state = str(uuid.uuid4())
        request.session['oauth_state'] = state

        print("\n" + "="*70)
        print("🚀 GOOGLE LOGIN INITIATED")
        print(f"📍 State: {state}")
        print(f"📍 Redirect URI: {REDIRECT_URI}")
        print("="*70 + "\n")

        google_url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={GOOGLE_CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            "&response_type=code"
            "&scope=openid%20email%20profile"
            "&access_type=offline"
            f"&state={state}"
            "&prompt=consent"
        )
        
        return redirect(google_url)
class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        print("\n" + "=" * 70)
        print("📥 GOOGLE CALLBACK RECEIVED")
        print(f"📍 URL: {request.build_absolute_uri()}")
        print("=" * 70 + "\n")

        state = request.GET.get("state")
        saved_state = request.session.get("oauth_state")

        if saved_state and state != saved_state:
            return self._error_response("INVALID_STATE")

        error = request.GET.get("error")
        if error:
            return self._error_response(f"GOOGLE_ERROR_{error}")

        code = request.GET.get("code")
        if not code:
            return self._error_response("NO_CODE")

        try:
            # Exchange code for access token
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )

            token_data = token_response.json()

            if token_response.status_code != 200:
                return self._error_response("TOKEN_EXCHANGE_FAILED")

            access_token = token_data.get("access_token")
            if not access_token:
                return self._error_response("NO_ACCESS_TOKEN")

            # Fetch user info
            user_info = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            ).json()

            email = user_info.get("email")
            name = user_info.get("name") or email.split("@")[0]

            if not email:
                return self._error_response("NO_EMAIL")

            # Create or fetch user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": name,
                    "role": "user",
                    "is_verified": True,
                    "is_active": True,
                },
            )

            refresh = RefreshToken.for_user(user)
            access_jwt = str(refresh.access_token)
            refresh_jwt = str(refresh)

            return self._success_response(access_jwt, refresh_jwt, email, name)

        except Exception as e:
            print("❌ ERROR:", e)
            return self._error_response("INTERNAL_ERROR")

    # ----------------------------------------------------------------------

    def _success_response(self, access_jwt, refresh_jwt, email, name):
        """Popup success page (clean + no warnings)"""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Login Successful</title>

<style>
    body {{
        margin:0;
        padding:0;
        height:100vh;
        display:flex;
        justify-content:center;
        align-items:center;
        background:linear-gradient(135deg,#4ade80,#22d3ee);
        font-family:Arial;
        color:white;
    }}
    .box {{
        padding:35px;
        text-align:center;
        background:rgba(255,255,255,0.15);
        border-radius:18px;
        backdrop-filter:blur(8px);
    }}
    .icon {{
        font-size:65px;
        margin-bottom:10px;
    }}
</style>
</head>

<body>
<div class="box">
    <div class="icon">✅</div>
    <h2>Login Successful!</h2>
    <p>Welcome, {name}!</p>
</div>

<script>
console.log("Popup loaded");

// ---------- Payload Object (NO WARNINGS) ----------
const payload = {{
    access_token: "{access_jwt}",
    refresh_token: "{refresh_jwt}",
    email: "{email}",
    name: "{name}"
}};

// ---------- Message wrapper ----------
const message = {{
    type: "GOOGLE_AUTH_SUCCESS",
    payload: payload
}};

// ---------- Send message to opener ----------
function sendMessage() {{
    try {{
        window.opener.postMessage(message, "http://localhost:5173");
        console.log("Message sent:", message);
        return true;
    }} catch (e) {{
        console.error("Message error:", e);
        return false;
    }}
}}

let sent = sendMessage();

// Retry after 300ms
setTimeout(() => {{
    if (!sent) {{
        console.log("Retrying message…");
        sendMessage();
    }}
}}, 300);

// Close popup after 1.8 sec
setTimeout(() => {{
    window.close();
}}, 1800);
</script>
</body>
</html>
"""
        return HttpResponse(html)

    # ----------------------------------------------------------------------

    def _error_response(self, error_msg):
        html = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Arial;text-align:center;padding-top:60px;">
    <h2>❌ Login Failed</h2>
    <p>Error: {error_msg}</p>

<script>
window.opener?.postMessage({{ type:"GOOGLE_AUTH_ERROR", error:"{error_msg}" }}, "http://localhost:5173");
setTimeout(() => window.close(), 1500);
</script>

</body>
</html>
"""
        return HttpResponse(html)



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        display_name = profile.display_name or ""
        name_parts = display_name.split(' ', 1)
        firstName = name_parts[0] if len(name_parts) > 0 else ""
        lastName = name_parts[1] if len(name_parts) > 1 else ""

        data = {
            "_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "createdAt": user.date_joined.isoformat(),
            "role": user.role,
            "bio" : profile.bio,
            "skills" : profile.skills or [],
            "display_name": display_name,
            "firstName": firstName,
            "lastName": lastName,
            "github": profile.github,
            "linkedin": profile.linkedin,
            "profileImage": profile.profileImage.url if profile.profileImage else None,
            "resume": profile.resume.url if profile.resume else None,
        }
        
        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)


class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        data = {
            "totalProblems": 150,
            "solvedProblems": getattr(profile, 'problems_solved', 0),
            "easyCount": 0,
            "mediumCount": 0,
            "hardCount": 0,
            "currentStreak": 0,
            "longestStreak": 0,
            "recentSubmissions": []
        }
        
        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)



GITHUB_CLIENT_ID = settings.GITHUB_CLIENT_ID
GITHUB_CLIENT_SECRET = settings.GITHUB_CLIENT_SECRET
GITHUB_REDIRECT_URI = "http://localhost:8000/api/auth/github/callback/"

class GitHubLoginView(APIView):
    permission_classes=[AllowAny]

    def get(self , request):
         
        state = str(uuid.uuid4())

         
        cache.set(
            f"github_oauth_state:{state}",
            "valid",
            timeout=600
        )

        github_url = (
            "https://github.com/login/oauth/authorize"
            f"?client_id={settings.GITHUB_CLIENT_ID}"
            f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
            "&scope= read:user  user:email"
            f"&state={state}"
        )
        return redirect(github_url)
    
class GitHubCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        print("\n=== 🐙 GITHUB CALLBACK RECEIVED ===")

        code = request.GET.get("code")
        state = request.GET.get("state")

         
        cache_key = f"github_oauth_state:{state}"
        stored_state = cache.get(cache_key)

        if not stored_state:
            print("❌ Invalid or expired state")
            return self._error_response("INVALID_STATE")

         
        cache.delete(cache_key)

        if not code:
            return self._error_response("NO_CODE")

        try:
             
            token_res = requests.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": GITHUB_REDIRECT_URI
                }
            ).json()

            github_access_token = token_res.get("access_token")

            if not github_access_token:
                return self._error_response("NO_ACCESS_TOKEN")

             
            user_res = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {github_access_token}"}
            ).json()

             
            email_res = requests.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {github_access_token}"}
            ).json()

             
            email = None
            for e in email_res:
                if e.get("primary") and e.get("verified"):
                    email = e["email"]
                    break

            if not email:
                return self._error_response("NO_VERIFIED_EMAIL")

            name = user_res.get("name") or user_res.get("login") or email.split("@")[0]

             
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": name,
                    "role": "user",
                    "is_verified": True,
                    "is_active": True,
                }
            )

             
            refresh = RefreshToken.for_user(user)
            access_jwt = str(refresh.access_token)
            refresh_jwt = str(refresh)

             
            return self._success_response(access_jwt, refresh_jwt, email, name)

        except Exception as e:
            print("❌ GitHub OAuth Error:", e)
            return self._error_response("SERVER_ERROR")
    def _success_response(self, access_jwt, refresh_jwt, email, name):
        html = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Arial; text-align:center; margin-top:60px;">

<h2> GitHub Login Successful!</h2>
<p>Welcome {name}</p>

<script>
const payload = {{
    access_token: "{access_jwt}",
    refresh_token: "{refresh_jwt}",
    email: "{email}",
    name: "{name}"
}};

window.opener?.postMessage(
    {{
        type: "GITHUB_AUTH_SUCCESS",
        payload: payload
    }},
    "http://localhost:5173"
);

setTimeout(() => window.close(), 1200);
</script>

</body>
</html>
"""
        return HttpResponse(html)

    def _error_response(self, error_msg):
        html = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Arial;text-align:center;margin-top:60px;">

<h2> GitHub Login Failed</h2>
<p>{error_msg}</p>

<script>
window.opener?.postMessage(
    {{ type: "GITHUB_AUTH_ERROR", error: "{error_msg}" }},
    "http://localhost:5173"
);
setTimeout(() => window.close(), 1200);
</script>

</body>
</html>
"""
        return HttpResponse(html)



User = get_user_model()

class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 5))
        search = request.GET.get("search")
        status = request.GET.get("status")

        users = User.objects.filter(role="user").order_by("-date_joined")

        if search:
            users = users.filter(email__icontains=search)

        if status == "active":
            users = users.filter(is_active=True)
        elif status == "blocked":
            users = users.filter(is_active=False)

        paginator = Paginator(users, limit)
        page_obj = paginator.get_page(page)

        data = []
        for u in page_obj:
            data.append({
                "_id": str(u.id),
                "username": u.username,
                "email": u.email,
                "status": "Active" if u.is_active else "InActive",
            })

        return Response({
            "success": True,
            "data": {
                "users": data,
                "pagination": {
                    "page": page,
                    "pages": paginator.num_pages,
                    "total": paginator.count,
                }
            }
        })
    
User = get_user_model()


class ToggleUserStatusView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if user.is_superuser:
            return Response(
                {"success": False, "message": "Cannot block admin"},
                status=400,
            )
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])

        return Response({
            "success": True,
            "message": "User status updated successfully",
            "data": {
                "_id": str(user.id),
                "status": "Active" if user.is_active else "InActive",
            }
        })

User = get_user_model()


class AdminRecruiterListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 5))
        search = request.GET.get("search")
        status = request.GET.get("status")

        recruiters = User.objects.filter(role="recruiter").order_by("-date_joined")
        print(recruiters)
        if search:
            recruiters = recruiters.filter(email__icontains=search)

        if status == "active":
            recruiters = recruiters.filter(is_active=True)
        elif status == "blocked":
            recruiters = recruiters.filter(is_active=False)

        paginator = Paginator(recruiters, limit)
        page_obj = paginator.get_page(page)

        data = [
            {
                "_id": str(r.id),
                "username": r.username,
                "email": r.email,
                "status": "Active" if r.is_active else "InActive",
            }
            for r in page_obj
        ]

        return Response({
            "success": True,
            "data": {
                "recruiters": data,
                "pagination": {
                    "page": page,
                    "pages": paginator.num_pages,
                    "total": paginator.count,
                },
            },
        })


class ToggleRecruiterStatusView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, recruiter_id):
        recruiter = get_object_or_404(User, id=recruiter_id, role="recruiter")

        recruiter.is_active = not recruiter.is_active
        recruiter.save(update_fields=["is_active"])

        return Response({
            "success": True,
            "data": {
                "_id": str(recruiter.id),
                "status": "Active" if recruiter.is_active else "InActive",
            },
        })
    