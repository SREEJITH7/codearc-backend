from django.urls import path
from .views import AdminApplicationListView, AdminDashboardMetricsView

urlpatterns = [
    path('applicants/', AdminApplicationListView.as_view(), name='admin-applicants'),
    path('dashboard/metrics/', AdminDashboardMetricsView.as_view(), name='admin-dashboard-metrics'),
]
