# apps/ai_app/services/ai_chat_service.py

import logging
from apps.ai_app.models import AiChatSession, AiChatMessage
from apps.ai_app.clients.groq_client import generate_ai_response
from apps.ai_app.utils.chat_builder import build_messages

logger = logging.getLogger(__name__)


def handle_ai_chat(user, message_content, session_id=None):
    try:
        if session_id:
            session = AiChatSession.objects.get(
                id=session_id,
                user=user
            )
        else:
            title = message_content[:30] + (
                "..." if len(message_content) > 30 else ""
            )
            session = AiChatSession.objects.create(
                user=user,
                title=title
            )

        AiChatMessage.objects.create(
            session=session,
            role="user",
            content=message_content
        )

        history = session.messages.all().order_by("created_at")
        messages = build_messages(history)

        response = generate_ai_response(messages)
        ai_reply = response.choices[0].message.content

        AiChatMessage.objects.create(
            session=session,
            role="assistant",
            content=ai_reply
        )

        return {
            "reply": ai_reply,
            "session": session
        }
    except AiChatSession.DoesNotExist:
        logger.error(f"Session {session_id} not found for user {user.id}")
        raise ValueError("Invalid session ID")
    except Exception as e:
        logger.error(f"Error in handle_ai_chat: {str(e)}", exc_info=True)
        raise e