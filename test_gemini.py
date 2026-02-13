import os
from google import genai
from django.conf import settings
import django

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

client = genai.Client(api_key=settings.GEMINI_API_KEY)

try:
    print("Testing gemini-2.0-flash...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Hello, how are you?"
    )
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
