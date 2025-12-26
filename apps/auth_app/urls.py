 

# apps/auth_app/urls.py

from django.urls import path
from .views.auth_views import (
    AdminLoginView,
    CookieTokenRefreshView,
    ForgotPasswordOTPView,
    GoogleCallbackView,
    GoogleLoginView,
    GitHubLoginView,
    GitHubCallbackView,
    LoginView,
    RecruiterLoginView,
    ResendOTPView,
    ResetPasswordView,
    SignupView,
    UserProfileView,
    UserStatsView,
    VerifyOTPView,
    # need to change this to another
    AdminUserListView,
    ToggleUserStatusView,
    AdminRecruiterListView,
    ToggleRecruiterStatusView,
    
)

from .views.logout import LogoutView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path("forgot-password/otp/", ForgotPasswordOTPView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),
    path("login/", LoginView.as_view(), name="login"),
    path("recruiter/login", RecruiterLoginView.as_view()),
    path("admin/login", AdminLoginView.as_view(), name="admin-login"),
    path("refresh-token/", CookieTokenRefreshView.as_view(), name="token_refresh"),

    # GOOGLE OAUTH — WITH /api/auth/ prefix
    path("google/login/", GoogleLoginView.as_view(), name="google-login"),
    path("google/callback/", GoogleCallbackView.as_view(), name="google-callback"),


    
    path("github/login/", GitHubLoginView.as_view(), name="github-login"),
    path("github/callback/", GitHubCallbackView.as_view(), name="github-callback"),

    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/stats/', UserStatsView.as_view(), name='user-stats'),

    path("userslist", AdminUserListView.as_view(), name="admin-users-list"),
    path("users/<uuid:user_id>/toggle-status", ToggleUserStatusView.as_view(), name="toggle-user-status"),
    path("recruiterslist", AdminRecruiterListView.as_view()),
    path("recruiters/<uuid:recruiter_id>/toggle-status", ToggleRecruiterStatusView.as_view()),

    path("logout/",LogoutView.as_view() , name ="logout"),
]   

