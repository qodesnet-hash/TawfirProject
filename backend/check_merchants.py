#!/usr/bin/env python
"""
Script to check merchant status
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings_simple')
django.setup()

from api.models import Merchant, MerchantRequest
from users.models import CustomUser

def check_merchants():
    print("=" * 50)
    print("📝 فحص حالة التجار")
    print("=" * 50)
    
    # عرض جميع المستخدمين
    print("\n👥 المستخدمون:")
    for user in CustomUser.objects.all():
        print(f"  - {user.phone_number} (ID: {user.id})")
    
    # عرض جميع طلبات التجار
    print("\n📋 طلبات التجار:")
    for req in MerchantRequest.objects.all():
        print(f"  - {req.business_name} ({req.user.phone_number}) - Status: {req.status}")
    
    # عرض جميع التجار
    print("\n🏪 التجار المسجلون:")
    for merchant in Merchant.objects.all():
        print(f"  - {merchant.business_name} ({merchant.user.phone_number}) - Status: {merchant.status}")
        
    print("\n" + "=" * 50)
    
    # اختبار مستخدم معين
    phone = input("أدخل رقم الهاتف للتحقق من حالته (أو اضغط Enter للخروج): ")
    if phone:
        try:
            user = CustomUser.objects.get(phone_number=phone)
            print(f"\n✅ المستخدم موجود: {user.phone_number}")
            
            # التحقق من الطلب
            try:
                req = MerchantRequest.objects.get(user=user)
                print(f"📋 حالة الطلب: {req.status}")
            except MerchantRequest.DoesNotExist:
                print("❌ لا يوجد طلب لهذا المستخدم")
            
            # التحقق من التاجر
            try:
                merchant = Merchant.objects.get(user=user)
                print(f"🏪 التاجر: {merchant.business_name}")
                print(f"   الحالة: {merchant.status}")
                print(f"   نشط؟: {'نعم' if merchant.status == 'مقبول' else 'لا'}")
            except Merchant.DoesNotExist:
                print("❌ ليس تاجراً")
                
        except CustomUser.DoesNotExist:
            print(f"❌ المستخدم برقم {phone} غير موجود")
    
    print("=" * 50)

if __name__ == '__main__':
    check_merchants()
