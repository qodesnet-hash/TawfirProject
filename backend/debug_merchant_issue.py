#!/usr/bin/env python
"""
سكريبت فحص وإصلاح مشكلة التاجر - Debug Merchant Issue
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from api.models import Merchant
from users.models import CustomUser
from django.contrib.auth import get_user_model

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       🔍 فحص مشكلة التاجر - Debug Merchant Issue         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # 1. عرض جميع المستخدمين التجار
    print("👥 المستخدمون من نوع 'merchant':")
    print("=" * 60)
    merchant_users = CustomUser.objects.filter(user_type='merchant')
    
    if not merchant_users.exists():
        print("⚠️  لا يوجد مستخدمون من نوع تاجر")
        print("\n💡 هل تريد إنشاء تاجر تجريبي؟ (y/n): ", end='')
        choice = input().strip().lower()
        if choice == 'y':
            create_test_merchant()
        return
    
    for user in merchant_users:
        print(f"\n📧 البريد: {user.email}")
        print(f"   الاسم: {user.full_name or 'غير محدد'}")
        print(f"   الهاتف: {user.phone_number or 'غير محدد'}")
        
        # البحث عن حساب تاجر مرتبط
        try:
            merchant = Merchant.objects.get(user=user)
            print(f"   ✅ لديه حساب تاجر:")
            print(f"      - ID: {merchant.id}")
            print(f"      - الاسم التجاري: {merchant.business_name}")
            print(f"      - الحالة: '{merchant.status}'")
            print(f"      - الحالة (hex): {merchant.status.encode('utf-8')}")
            
            # التحقق من المشكلة
            if merchant.status != 'مقبول':
                print(f"      ⚠️  الحالة ليست 'مقبول' بالضبط!")
                print(f"      💡 هل تريد تغيير الحالة إلى 'مقبول'؟ (y/n): ", end='')
                choice = input().strip().lower()
                if choice == 'y':
                    merchant.status = 'مقبول'
                    merchant.save()
                    print(f"      ✅ تم تحديث الحالة بنجاح!")
            else:
                print(f"      ✅ الحالة صحيحة!")
                
        except Merchant.DoesNotExist:
            print(f"   ❌ لا يوجد حساب تاجر مرتبط!")
            print(f"   💡 هل تريد إنشاء حساب تاجر لهذا المستخدم؟ (y/n): ", end='')
            choice = input().strip().lower()
            if choice == 'y':
                create_merchant_for_user(user)
    
    print("\n" + "=" * 60)
    
    # 2. فحص جميع التجار
    print("\n🏪 جميع التجار في النظام:")
    print("=" * 60)
    all_merchants = Merchant.objects.all()
    
    for merchant in all_merchants:
        print(f"\n🏪 {merchant.business_name}")
        print(f"   البريد: {merchant.user.email}")
        print(f"   الحالة: '{merchant.status}'")
        print(f"   الحالة الصحيحة: {merchant.status == 'مقبول'}")
        
        # اختبار الاستعلام
        test_query = Merchant.objects.filter(user=merchant.user, status='مقبول')
        if test_query.exists():
            print(f"   ✅ يمكن الوصول إليه بالاستعلام")
        else:
            print(f"   ❌ لا يمكن الوصول إليه بالاستعلام!")
            print(f"   🔧 يحتاج إصلاح...")
    
    print("\n" + "=" * 60)
    print("✅ انتهى الفحص!")
    print("\n💡 الخطوات التالية:")
    print("   1. إذا تم إصلاح أي مشكلة، أعد تشغيل الخادم")
    print("   2. جرب إنشاء عرض من التطبيق")
    print("   3. راجع ملف error.log إذا استمرت المشكلة")

def create_test_merchant():
    """إنشاء تاجر تجريبي"""
    print("\n📝 إنشاء تاجر تجريبي...")
    
    email = input("أدخل البريد الإلكتروني: ").strip()
    if not email:
        email = 'test-merchant@example.com'
    
    password = input("أدخل كلمة المرور: ").strip()
    if not password:
        password = 'test123'
    
    try:
        # إنشاء المستخدم
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            full_name='تاجر تجريبي',
            user_type='merchant',
            phone_number='0500000000'
        )
        print(f"✅ تم إنشاء المستخدم: {email}")
        
        # إنشاء التاجر
        merchant = Merchant.objects.create(
            user=user,
            business_name='متجر تجريبي',
            status='مقبول',
            phone='0500000000',
            address='عنوان تجريبي'
        )
        print(f"✅ تم إنشاء التاجر: {merchant.business_name}")
        print(f"\n📋 معلومات الدخول:")
        print(f"   البريد: {email}")
        print(f"   كلمة المرور: {password}")
        
    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")

def create_merchant_for_user(user):
    """إنشاء حساب تاجر لمستخدم موجود"""
    print(f"\n📝 إنشاء حساب تاجر لـ {user.email}...")
    
    business_name = input("أدخل الاسم التجاري: ").strip()
    if not business_name:
        business_name = f"متجر {user.full_name or user.email}"
    
    try:
        merchant = Merchant.objects.create(
            user=user,
            business_name=business_name,
            status='مقبول',
            phone=user.phone_number or '0500000000',
            address='عنوان المتجر'
        )
        print(f"✅ تم إنشاء حساب تاجر: {merchant.business_name}")
        
    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  تم إلغاء العملية")
    except Exception as e:
        print(f"\n❌ حدث خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
