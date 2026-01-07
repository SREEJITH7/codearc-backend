


from django.urls import path
from .views import (
    AdminProblemCreateView,
    AdminTestCaseCreateView,
    ProblemListView,
    ProblemDetailView,
    ProblemToggleView, # Added
    CategoryCreateView,
    CategoryListView,
    CategoryToggleView,
    CategoryUpdateView,
    ProblemDeleteView,
)

urlpatterns = [
    path("admin/problems/", AdminProblemCreateView.as_view()),
    path("admin/problems/<int:problem_id>/testcases/", AdminTestCaseCreateView.as_view()),
    path("admin/problems/<int:problem_id>/delete/", ProblemDeleteView.as_view()),
    
    path("problems/", ProblemListView.as_view()),
    path("problems/<int:problem_id>/", ProblemDetailView.as_view()),
    path("problems/<int:problem_id>/toggle/", ProblemToggleView.as_view()), # Added

    # Category endpoints - MOVED TO ROOT LEVEL
    path("categorylist/", CategoryListView.as_view(), name="category-list-all"),
    path("addcategory/", CategoryCreateView.as_view(), name="category-create"),
    path("categorylist/", CategoryListView.as_view(), name="category-list-paginated"),
    path("updatecategory/<int:category_id>/", CategoryUpdateView.as_view(), name="category-update"),
    path("category/<int:category_id>/", CategoryToggleView.as_view(), name="category-toggle"),
]







