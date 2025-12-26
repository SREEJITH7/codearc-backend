from django.urls import path
from .views.profile_views import RecruiterProfileView

urlpatterns = [
    path("profile/", RecruiterProfileView.as_view()),
        
]
