#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from users.models import CustomUser

print("=== جميع المستخدمين في قاعدة البيانات ===\n")

users = CustomUser.objects.all()

if not users:
    print("لا يوجد مستخدمين")
else:
    for user in users:
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Phone: {user.phone_number}")
        print(f"Full Name: {user.full_name}")
        print(f"City: {user.city}")
        print(f"User Type: {user.user_type}")
        print(f"Needs Completion: {user.needs_profile_completion}")
        print("-" * 50)

print(f"\nإجمالي المستخدمين: {users.count()}")
