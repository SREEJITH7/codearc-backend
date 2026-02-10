from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.profile_views import RecruiterProfileView
from .views.recruiter_job import RecruiterJobViewSet
from .views.public_jobs import PublicJobListView
from .views.recruiter_applicants import RecruiterApplicantsListView
from .views.recruiter_applicant_detail import RecruiterApplicationDetailView
from .views.recruiter_applicant_detail import RecruiterUpdateApplicationStatusView
from .views.recruiter_user_profile import RecruiterUserProfileView
from .views.recruiter_send_offer import RecruiterSendOfferView

router = DefaultRouter()
router.register(r'jobs', RecruiterJobViewSet, basename='recruiter-jobs')

urlpatterns = [
    path("profile/", RecruiterProfileView.as_view()),
    path("jobs/public", PublicJobListView.as_view()),
    path("applicants/", RecruiterApplicantsListView.as_view()),
    path("applicants/<int:application_id>/", RecruiterApplicationDetailView.as_view()),
    path("applicants/<int:application_id>/status/", RecruiterUpdateApplicationStatusView.as_view()),
    path("applicants/<int:application_id>/send-offer/", RecruiterSendOfferView.as_view()),
    path("users/<int:user_id>/profile/", RecruiterUserProfileView.as_view()),

    path("", include(router.urls)),

]
