from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from django.conf import settings

from groq import Groq

from apps.ai_app.utils.prompts import AI_TUTOR_SYSTEM_PROMPT
from apps.ai_app.models import AiChatSession, AiChatMessage
from apps.ai_app.serializers import (
    AiChatSessionSerializer,
    AiChatSessionListSerializer,
)


# Initialize Groq client once
groq_client = Groq(api_key=settings.GROQ_API_KEY)


class AiChatThrottle(UserRateThrottle):
    scope = "ai_chat"
    rate = "20/day"


class AiChatView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AiChatThrottle]

    def post(self, request):
        message_content = request.data.get("message")
        session_id = request.data.get("session_id")

        if not message_content:
            return Response(
                {"success": False, "message": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create session
        if session_id:
            try:
                session = AiChatSession.objects.get(
                    id=session_id,
                    user=request.user
                )
            except (AiChatSession.DoesNotExist, ValueError):
                return Response(
                    {"success": False, "message": "Invalid session ID"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            title = message_content[:30] + (
                "..." if len(message_content) > 30 else ""
            )
            session = AiChatSession.objects.create(
                user=request.user,
                title=title
            )

        # Save user message
        AiChatMessage.objects.create(
            session=session,
            role="user",
            content=message_content
        )

        # Build conversation history (chronological)
        history = (
            session.messages
            .all()
            .order_by("created_at")
        )

        messages = [
            {"role": "system", "content": AI_TUTOR_SYSTEM_PROMPT}
        ]

        for msg in history:
            messages.append(
                {"role": msg.role, "content": msg.content}
            )

        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Working stable model
                messages=messages,
                temperature=0.3,
                max_tokens=800,
            )

            ai_reply = response.choices[0].message.content

            # Save AI reply
            AiChatMessage.objects.create(
                session=session,
                role="assistant",
                content=ai_reply
            )

            return Response(
                {
                    "success": True,
                    "reply": ai_reply,
                    "session_id": session.id,
                    "session_title": session.title
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Groq API Error: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Groq API error",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AiSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = AiChatSession.objects.filter(user=request.user)
        serializer = AiChatSessionListSerializer(sessions, many=True)
        return Response(serializer.data)


class AiSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = AiChatSession.objects.get(
                id=session_id,
                user=request.user
            )
            serializer = AiChatSessionSerializer(session)
            return Response(serializer.data)
        except (AiChatSession.DoesNotExist, ValueError):
            return Response(
                {"message": "Session not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, session_id):
        try:
            session = AiChatSession.objects.get(
                id=session_id,
                user=request.user
            )
            session.delete()
            return Response(
                {"success": True},
                status=status.HTTP_204_NO_CONTENT
            )
        except (AiChatSession.DoesNotExist, ValueError):
            return Response(
                {"message": "Session not found"},
                status=status.HTTP_404_NOT_FOUND
            )
