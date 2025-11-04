#!/usr/bin/env python
"""
إصلاح فوري لمشكلة حالة التاجر
Immediate fix for merchant status issue
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from api.models import Merchant
from users.models import CustomUser

def fix_all_merchants():
    print("=" * 60)
    print("  🔧 إصلاح فوري لحالة التجار")
    print("=" * 60)
    print()
    
    merchants = Merchant.objects.all()
    
    if not merchants.exists():
        print("❌ لا يوجد تجار في النظام!")
        print("\n💡 هل تريد إنشاء تاجر تجريبي؟")
        response = input("اكتب 'y' للموافقة: ")
        if response.lower() == 'y':
            create_test_merchant()
        return
    
    print(f"📊 وجد {merchants.count()} تاجر في النظام\n")
    
    fixed_count = 0
    
    for merchant in merchants:
        print(f"🏪 {merchant.business_name}")
        print(f"   الحالة الحالية: '{merchant.status}'")
        
        if merchant.status != 'مقبول':
            merchant.status = 'مقبول'
            merchant.save()
            print(f"   ✅ تم تحديث الحالة إلى: 'مقبول'")
            fixed_count += 1
        else:
            print(f"   ✅ الحالة صحيحة بالفعل")
        print()
    
    if fixed_count > 0:
        print(f"✅ تم إصلاح {fixed_count} تاجر")
    else:
        print("✅ جميع التجار لديهم حالة صحيحة")
    
    print("\n" + "=" * 60)
    print("  📋 النتيجة النهائية")
    print("=" * 60)
    
    for merchant in merchants:
        status_icon = "✅" if merchant.status == 'مقبول' else "❌"
        print(f"{status_icon} {merchant.business_name}: {merchant.status}")
    
    print("\n✅ الإصلاح مكتمل!")
    print("💡 الآن جرب إضافة عرض من التطبيق")

def create_test_merchant():
    """إنشاء تاجر تجريبي"""
    print("\n📝 إنشاء تاجر تجريبي...\n")
    
    email = input("البريد الإلكتروني (test@tawfir.com): ").strip() or "test@tawfir.com"
    business_name = input("اسم المتجر (متجر تجريبي): ").strip() or "متجر تجريبي"
    
    # إنشاء أو جلب المستخدم
    user, created = CustomUser.objects.get_or_create(
        email=email,
        defaults={
            'full_name': 'تاجر تجريبي',
            'user_type': 'merchant',
            'is_active': True,
            'is_verified': True
        }
    )
    
    if created:
        user.set_password('test123')
        user.save()
        print(f"✅ تم إنشاء مستخدم: {email}")
    else:
        print(f"✅ المستخدم موجود: {email}")
    
    # إنشاء أو تحديث التاجر
    merchant, created = Merchant.objects.update_or_create(
        user=user,
        defaults={
            'business_name': business_name,
            'status': 'مقبول',
            'phone': '0500000000',
            'address': 'عنوان تجريبي'
        }
    )
    
    if created:
        print(f"✅ تم إنشاء تاجر: {business_name}")
    else:
        print(f"✅ تم تحديث التاجر: {business_name}")
    
    print(f"\n🎉 التاجر جاهز!")
    print(f"   📧 البريد: {email}")
    print(f"   🔑 كلمة المرور: test123")
    print(f"   📊 الحالة: {merchant.status}")

if __name__ == '__main__':
    try:
        fix_all_merchants()
    except Exception as e:
        print(f"\n❌ حدث خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
