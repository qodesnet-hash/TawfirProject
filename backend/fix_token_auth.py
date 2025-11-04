#!/usr/bin/env python
"""
سكربت لفحص وإصلاح مشكلة Token Authentication
يجب تشغيله باستخدام Django shell:
python manage.py shell < fix_token_auth.py
"""

import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from rest_framework.authtoken.models import Token
from users.models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*60)
print("🔍 فحص نظام Token Authentication")
print("="*60)

# 1. فحص المستخدمين
print("\n📱 المستخدمون المسجلون:")
users = User.objects.all()
for user in users[:5]:  # أول 5 مستخدمين
    print(f"  - User #{user.id}: {user.phone_number}")
    
    # فحص التوكن
    try:
        token = Token.objects.get(user=user)
        print(f"    ✅ Token: {token.key[:20]}...")
    except Token.DoesNotExist:
        print(f"    ⚠️ لا يوجد توكن - سيتم إنشاء واحد...")
        token = Token.objects.create(user=user)
        print(f"    ✅ تم إنشاء Token: {token.key[:20]}...")

# 2. اختبار مستخدم محدد
phone = input("\n📱 أدخل رقم الهاتف للاختبار (أو اضغط Enter للتخطي): ")
if phone:
    try:
        user = User.objects.get(phone_number=phone)
        print(f"\n✅ تم العثور على المستخدم: {user.phone_number}")
        
        # التأكد من وجود توكن
        token, created = Token.objects.get_or_create(user=user)
        if created:
            print(f"✅ تم إنشاء توكن جديد")
        else:
            print(f"✅ التوكن موجود مسبقاً")
        
        print(f"\n🎫 Token للاستخدام في الاختبارات:")
        print(f"   {token.key}")
        
        print(f"\n📋 كيفية استخدام Token:")
        print(f"   Header: Authorization")
        print(f"   Value:  Token {token.key}")
        
    except User.DoesNotExist:
        print(f"❌ لم يتم العثور على مستخدم برقم: {phone}")

# 3. فحص إعدادات REST Framework
print("\n⚙️ إعدادات REST Framework:")
from django.conf import settings
auth_classes = settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES', [])
print(f"   Authentication Classes: {auth_classes}")

if 'rest_framework.authentication.TokenAuthentication' in auth_classes:
    print("   ✅ TokenAuthentication مفعل")
else:
    print("   ⚠️ TokenAuthentication غير مفعل!")

print("\n" + "="*60)
print("✅ انتهى الفحص")
print("="*60)
