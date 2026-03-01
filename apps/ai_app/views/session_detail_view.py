# apps/ai_app/views/session_detail_view.py

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.ai_app.models import AiChatSession
from apps.ai_app.serializers import AiChatSessionSerializer

logger = logging.getLogger(__name__)


class AiSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = AiChatSession.objects.get(
                id=session_id,
                user=request.user
            )
        except AiChatSession.DoesNotExist:
            return Response(
                {"success": False, "message": "Session not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AiChatSessionSerializer(session)

        return Response({
            "success": True,
            "data": serializer.data
        })

    def delete(self, request, session_id):
        try:
            session = AiChatSession.objects.get(
                id=session_id,
                user=request.user
            )
            session.delete()
            return Response(
                {"success": True, "message": "Session deleted"},
                status=status.HTTP_200_OK
            )
        except AiChatSession.DoesNotExist:
            return Response(
                {"success": False, "message": "Session not found"},
                status=status.HTTP_404_NOT_FOUND
            )