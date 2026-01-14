


from django.urls import path
from .views import (
    AdminProblemCreateView,
    ProblemUpdateView,
    ProblemListView,
    ProblemDetailView,
    ProblemToggleView, # Added
    CategoryCreateView,
    CategoryListView,
    CategoryToggleView,
    CategoryUpdateView,
    ProblemDeleteView,
    RunCodeView,
    SubmitCodeView,
    UserSubmissionsView, # Added
    AllSubmissionsView,
)

urlpatterns = [
    path("admin/problems/", AdminProblemCreateView.as_view()),
    path("admin/problems/<int:problem_id>/", ProblemUpdateView.as_view()),
    path("admin/problems/<int:problem_id>/delete/", ProblemDeleteView.as_view()),
    
    path("problems/", ProblemListView.as_view()),
    path("problems/<int:problem_id>/", ProblemDetailView.as_view()),
    path("problems/<int:problem_id>/toggle/", ProblemToggleView.as_view()),  
    path("admin/problems/<int:problem_id>/delete/", ProblemDeleteView.as_view()),


    # Category endpoints - MOVED TO ROOT LEVEL
    path("categorylist/", CategoryListView.as_view(), name="category-list-all"),
    path("addcategory/", CategoryCreateView.as_view(), name="category-create"),
    path("categorylist/", CategoryListView.as_view(), name="category-list-paginated"),
    path("updatecategory/<int:category_id>/", CategoryUpdateView.as_view(), name="category-update"),
    path("category/<int:category_id>/", CategoryToggleView.as_view(), name="category-toggle"),

    path("problems/run/", RunCodeView.as_view(), name = "run-code"),
    path("problems/submit/", SubmitCodeView.as_view(), name="submit-code"),
    path("problems/<int:problem_id>/submissions/me/", UserSubmissionsView.as_view(), name="user-submissions"),
    path("problems/<int:problem_id>/submissions/", AllSubmissionsView.as_view(), name="all-submissions"),
]







