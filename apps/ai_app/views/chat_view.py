# apps/ai_app/views/chat_view.py

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.ai_app.services.ai_chat_service import handle_ai_chat
from apps.ai_app.throttles.ai_chat_throttle import AiChatThrottle

logger = logging.getLogger(__name__)


class AiChatView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AiChatThrottle]

    def post(self, request):
        # Check subscription/usage limits
        from apps.subscription_app.services.subscription_service import can_use_ai_tutor
        allowed, info = can_use_ai_tutor(request.user)
        
        if not allowed:
            return Response(
                {"success": False, "message": info.get("message")},
                status=status.HTTP_403_FORBIDDEN
            )

        message_content = request.data.get("message")
        session_id = request.data.get("session_id")

        if not message_content:
            return Response(
                {"success": False, "message": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = handle_ai_chat(
                request.user,
                message_content,
                session_id
            )

            return Response(
                {
                    "success": True,
                    "reply": result["reply"],
                    "session_id": result["session"].id,
                    "session_title": result["session"].title
                },
                status=status.HTTP_200_OK
            )

        except ValueError as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"AI Chat error: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "message": "AI processing failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )