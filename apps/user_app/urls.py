from django.urls import path 
from apps.user_app.views.profile_views import UserProfileUpdateView

urlpatterns = [
    path("profile/update/<uuid:user_id>/",UserProfileUpdateView.as_view(), name = "profile-update"),
]





