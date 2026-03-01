# apps/ai_app/clients/groq_client.py

from groq import Groq
from django.conf import settings

groq_client = Groq(api_key=settings.GROQ_API_KEY)


def generate_ai_response(messages):
    return groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.3,
        max_tokens=800,
    )