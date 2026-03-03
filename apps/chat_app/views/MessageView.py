from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from ..serializer import   MessageSerializer
from ..models import Conversation, Message
from ..permissions import IsConversationParticipant



class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated ,IsConversationParticipant]

    def get_queryset(self):
        conversation_id = self.request.query_params.get("conv_id")
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if not (
            self.request.user == conversation.user or
            self.request.user == conversation.recruiter
        ):
            return Message.objects.none()

        return Message.objects.filter(conversation=conversation)

    def perform_create(self, serializer):
        conversation_id = self.request.data.get("conversation")
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if not (
            self.request.user == conversation.user or
            self.request.user == conversation.recruiter
        ):
            raise PermissionDenied("Not allowed")

        serializer.save(sender=self.request.user)