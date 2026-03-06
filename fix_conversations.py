import os
import sys
import django

# Add the project root to sys.path
sys.path.append('c:\\Users\\karnj\\OneDrive\\Desktop\\codeArc.main\\codearc-backend')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
    from apps.chat_app.models import Conversation
    from apps.recruiter_app.models import Application

    shortlisted = Application.objects.filter(status='SHORTLISTED')
    print(f"Found {shortlisted.count()} shortlisted applications.")
    
    count = 0
    for app in shortlisted:
        conv, created = Conversation.objects.get_or_create(
            application=app,
            defaults={
                'user': app.user,
                'recruiter': app.job.recruiter
            }
        )
        if created:
            count += 1
            print(f"Created conversation for app: {app.name}")

    print(f"Total mission conversations created: {count}")
except Exception as e:
    print(f"Error: {e}")
