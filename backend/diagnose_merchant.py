#!/usr/bin/env python
"""
سكريبت تشخيص سريع لمشكلة 403 Forbidden
Quick diagnostic script for 403 Forbidden issue
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from api.models import Merchant
from users.models import CustomUser

def diagnose_merchant_issue():
    print("=" * 60)
    print("  🔍 تشخيص مشكلة إضافة العروض - Diagnose Offer Creation Issue")
    print("=" * 60)
    print()
    
    # عرض جميع التجار
    merchants = Merchant.objects.all()
    
    if not merchants.exists():
        print("❌ لا يوجد تجار في النظام!")
        print("💡 قم بإنشاء تاجر عبر Django Admin أو سكريبت create_test_merchant.py")
        return
    
    print(f"📊 إجمالي التجار: {merchants.count()}\n")
    
    for merchant in merchants:
        print("-" * 60)
        print(f"🏪 التاجر: {merchant.business_name}")
        print(f"   📧 البريد: {merchant.user.email}")
        print(f"   📱 الهاتف: {merchant.phone or 'غير محدد'}")
        print(f"   📍 الحالة الحالية: '{merchant.status}'")
        print(f"   ✅ نوع الحالة: {type(merchant.status)}")
        
        # التحقق من الحالة
        if merchant.status == 'مقبول':
            print(f"   ✅ الحالة صحيحة ومتطابقة!")
        else:
            print(f"   ❌ الحالة غير مقبول!")
            print(f"   💡 تحتاج إلى تغيير الحالة إلى 'مقبول'")
        
        # التحقق من STATUS_CHOICES
        print(f"\n   📋 الخيارات المتاحة:")
        for choice_value, choice_label in Merchant.STATUS_CHOICES:
            if merchant.status == choice_value:
                print(f"      ✅ '{choice_value}' - {choice_label}")
            else:
                print(f"      ⭕ '{choice_value}' - {choice_label}")
        
        # التحقق من المستخدم
        print(f"\n   👤 معلومات المستخدم:")
        print(f"      - نوع المستخدم: {merchant.user.user_type}")
        print(f"      - نشط: {merchant.user.is_active}")
        print(f"      - موثق: {merchant.user.is_verified}")
        
        # التحقق من العروض
        offers_count = merchant.offer_set.count()
        print(f"\n   📦 عدد العروض: {offers_count}")
        
        print()
    
    print("\n" + "=" * 60)
    print("  💡 التوصيات")
    print("=" * 60)
    
    # التحقق من وجود تجار غير معتمدين
    non_approved = merchants.exclude(status='مقبول')
    if non_approved.exists():
        print(f"\n⚠️  يوجد {non_approved.count()} تاجر بحالة غير 'مقبول':")
        for m in non_approved:
            print(f"   - {m.business_name}: '{m.status}'")
        print("\n💡 لإصلاح ذلك، شغّل:")
        print("   python fix_merchant_status_now.py")
    else:
        print("\n✅ جميع التجار معتمدين (status='مقبول')")
        print("\nإذا كانت المشكلة ما زالت موجودة:")
        print("   1. تحقق من Token في التطبيق")
        print("   2. راجع ملف error.log")
        print("   3. افحص Network tab في Chrome DevTools")

if __name__ == '__main__':
    try:
        diagnose_merchant_issue()
    except Exception as e:
        print(f"\n❌ حدث خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
