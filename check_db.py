import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.chat_app.models import Conversation
from apps.recruiter_app.models import Application
from apps.auth_app.models import User

def check_data():
    print("--- Database Check ---")
    users = User.objects.all()
    print(f"Total Users: {users.count()}")
    for u in users:
        print(f"User: {u.email}, Role: {u.role}")

    apps = Application.objects.all()
    print(f"\nTotal Applications: {apps.count()}")
    for a in apps:
        print(f"App ID: {a.id}, Candidate: {a.user.email}, Job: {a.job.title}, Status: {a.status}")

    convs = Conversation.objects.all()
    print(f"\nTotal Conversations: {convs.count()}")
    for c in convs:
        print(f"Conv ID: {c.id}, App ID: {c.application.id}, Recruiter: {c.recruiter.email}, Candidate: {c.user.email}")

if __name__ == "__main__":
    check_data()
