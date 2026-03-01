from django.urls import path
# from .views.ai_chat import AiChatView, AiSessionListView, AiSessionDetailView
from .views.chat_view import AiChatView
from .views.session_detail_view import AiSessionDetailView
from .views.session_list_view import AiSessionListView


urlpatterns = [
    path('chat/', AiChatView.as_view()),
    path('sessions/', AiSessionListView.as_view()),
    path('sessions/<uuid:session_id>/', AiSessionDetailView.as_view()),
]