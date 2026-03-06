from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import models


from ..models import Conversation
from ..serializer import ConversationSerializer, MessageSerializer
import logging
from apps.recruiter_app.models import Application

logger = logging.getLogger(__name__)

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            models.Q(user=user) | models.Q(recruiter=user)
        ).select_related("user", "recruiter", "recruiter__recruiter_profile").order_by("-created_at")

    def list(self, request, *args, **kwargs):
        user = request.user
        logger.info(f"--- DEBUG CHAT ---")
        logger.info(f"User: {user.email}, ID: {user.id}, Role: {getattr(user, 'role', 'N/A')}")
        
        # Self-healing: Ensure all shortlisted/accepted applications have a conversation
        shortlisted_apps = Application.objects.filter(
            status__in=['SHORTLISTED', 'ACCEPTED']
        ).filter(
            models.Q(user=user) | models.Q(job__recruiter=user)
        )
        
        logger.info(f"Shortlisted apps found: {shortlisted_apps.count()}")
        
        for app in shortlisted_apps:
            conv, created = Conversation.objects.get_or_create(
                application=app,
                defaults={
                    'user': app.user,
                    'recruiter': app.job.recruiter
                }
            )
            logger.info(f"App {app.id}: Conversation {conv.id}, Created now: {created}")
            
        response = super().list(request, *args, **kwargs)
        
        # Log result
        if isinstance(response.data, dict) and 'results' in response.data:
            logger.info(f"Returning {len(response.data['results'])} paginated conversations.")
        elif isinstance(response.data, list):
            logger.info(f"Returning {len(response.data)} conversations.")
        else:
            logger.info(f"Returning unusual response data: {type(response.data)}")
            
        logger.info(f"--- END DEBUG ---")
        return response

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    