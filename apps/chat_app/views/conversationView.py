from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404


from ..models import Conversation
from ..serializer import ConversationSerializer, MessageSerializer
from ..permissions import IsConversationParticipant


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user
        ) | Conversation.objects.filter(
            recruiter=self.request.user
        )
    
    