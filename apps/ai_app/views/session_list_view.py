# apps/ai_app/views/session_list_view.py

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.ai_app.models import AiChatSession
from apps.ai_app.serializers import AiChatSessionListSerializer

logger = logging.getLogger(__name__)


class AiSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = AiChatSession.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = AiChatSessionListSerializer(sessions, many=True)

        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)