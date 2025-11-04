#!/usr/bin/env python
"""
سكريبت لإصلاح مشكلة حالة التاجر وتطبيق التحديثات
Script to fix Merchant status issue and apply updates
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from api.models import Merchant, MerchantRequest
from django.contrib.auth import get_user_model

User = get_user_model()

def main():
    print("🔧 بدء عملية إصلاح حالة التجار...")
    print("=" * 50)
    
    # 1. عرض جميع التجار وحالاتهم
    print("\n📊 قائمة التجار الحاليين:")
    merchants = Merchant.objects.all()
    
    if not merchants.exists():
        print("⚠️  لا يوجد تجار في النظام حالياً")
    else:
        for merchant in merchants:
            print(f"  - {merchant.business_name}")
            print(f"    الحالة: {merchant.status}")
            print(f"    المستخدم: {merchant.user.email}")
            print()
    
    # 2. التحقق من طلبات التجار
    print("\n📋 طلبات التجار:")
    requests = MerchantRequest.objects.all()
    
    if not requests.exists():
        print("⚠️  لا توجد طلبات للتجار")
    else:
        for req in requests:
            print(f"  - {req.business_name}")
            print(f"    الحالة: {req.status}")
            print(f"    المستخدم: {req.user.email}")
            print()
    
    # 3. تحديث التجار ذوي الحالة غير الصحيحة
    print("\n🔄 تحديث حالات التجار...")
    updated_count = 0
    
    for merchant in merchants:
        if merchant.status not in ['قيد المراجعة', 'مقبول', 'مرفوض']:
            print(f"  ⚠️  حالة غير صحيحة للتاجر: {merchant.business_name}")
            print(f"     الحالة الحالية: '{merchant.status}'")
            
            # السؤال عن التحديث
            response = input(f"     هل تريد تعيين الحالة إلى 'مقبول'؟ (y/n): ")
            if response.lower() == 'y':
                merchant.status = 'مقبول'
                merchant.save()
                print(f"     ✅ تم تحديث الحالة إلى 'مقبول'")
                updated_count += 1
            else:
                print(f"     ⏭️  تم تخطي التحديث")
    
    if updated_count > 0:
        print(f"\n✅ تم تحديث {updated_count} تاجر بنجاح")
    else:
        print("\n✅ جميع التجار لديهم حالات صحيحة")
    
    # 4. إحصائيات نهائية
    print("\n📊 إحصائيات التجار:")
    total = merchants.count()
    pending = merchants.filter(status='قيد المراجعة').count()
    approved = merchants.filter(status='مقبول').count()
    rejected = merchants.filter(status='مرفوض').count()
    
    print(f"  الإجمالي: {total}")
    print(f"  قيد المراجعة: {pending}")
    print(f"  مقبول: {approved}")
    print(f"  مرفوض: {rejected}")
    
    print("\n" + "=" * 50)
    print("✅ اكتملت عملية الإصلاح بنجاح!")
    print("\n💡 الخطوات التالية:")
    print("  1. تشغيل: python manage.py makemigrations")
    print("  2. تشغيل: python manage.py migrate")
    print("  3. إعادة تشغيل الخادم: python manage.py runserver")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ حدث خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
