#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from users.models import CustomUser

print("حذف المستخدم mar110fk@gmail.com...")

try:
    user = CustomUser.objects.get(email='mar110fk@gmail.com')
    print(f"وجدنا المستخدم: {user.email} (ID: {user.id})")
    user.delete()
    print("✅ تم الحذف بنجاح!")
except CustomUser.DoesNotExist:
    print("❌ المستخدم غير موجود")
except Exception as e:
    print(f"❌ خطأ: {e}")
