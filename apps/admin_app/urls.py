from django.urls import path
from .views import AdminApplicationListView

urlpatterns = [
    path('applicants/', AdminApplicationListView.as_view(), name='admin-applicants'),
]
