# apps/ai_app/utils/chat_builder.py

from apps.ai_app.utils.prompts import AI_TUTOR_SYSTEM_PROMPT

def build_messages(history):
    """
    Constructs the message payload for the Groq API.
    """
    messages = [
        {"role": "system", "content": AI_TUTOR_SYSTEM_PROMPT}
    ]

    for msg in history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    return messages