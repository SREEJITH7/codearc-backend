from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.conversationView import ConversationViewSet
from .views.MessageView import MessageViewSet
from .views.notification_view import NotificationViewSet

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversations")
router.register(r"messages", MessageViewSet, basename="messages")
router.register(r"notifications", NotificationViewSet, basename="notifications")

urlpatterns = router.urls
