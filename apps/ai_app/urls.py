from django.urls import path
from .views.ai_chat import AiChatView, AiSessionListView, AiSessionDetailView

urlpatterns = [
    path('chat/', AiChatView.as_view()),
    path('sessions/', AiSessionListView.as_view()),
    path('sessions/<uuid:session_id>/', AiSessionDetailView.as_view()),
]


