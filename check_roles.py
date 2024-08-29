import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Trial.settings')
django.setup()

from app1.models import UserProfile

tech_support_users = UserProfile.objects.filter(role='tech_support')
if not tech_support_users.exists():
    print("No users with the role 'tech_support' found.")
else:
    for user in tech_support_users:
        print(user.user.username)
