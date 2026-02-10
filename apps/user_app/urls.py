from django.urls import path 
from apps.user_app.views.profile_views import UserProfileUpdateView
from apps.user_app.views.user_jobs import UserJobListView, SingleJobView, JobApplicationView

urlpatterns = [
    path("profile/update/<uuid:user_id>/", UserProfileUpdateView.as_view(), name="profile-update"),
    path("jobs/", UserJobListView.as_view(), name="user-jobs"),
    path("jobs/<int:job_id>/", SingleJobView.as_view(), name="single-job"),
    path("applications/", JobApplicationView.as_view(), name="job-application"),
]





