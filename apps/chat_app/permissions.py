from rest_framework.permissions import BasePermission
from .models import Conversation


class IsConversationParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.user or
            request.user == obj.recruiter
        )
    