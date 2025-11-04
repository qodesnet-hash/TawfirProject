#!/usr/bin/env python
"""
اختبار API مباشرة - Test API Directly
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from django.test import RequestFactory
from rest_framework.test import force_authenticate
from api.merchant_views import MerchantOfferCreateView, CheckMerchantStatusView
from api.models import Merchant, City
from users.models import CustomUser

def test_merchant_api():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          🧪 اختبار API مباشرة - Direct API Test          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # 1. البحث عن تاجر
    print("[1] البحث عن تاجر...")
    merchants = Merchant.objects.all()
    
    if not merchants.exists():
        print("❌ لا يوجد تجار في النظام!")
        print("💡 قم بتشغيل: python debug_merchant_issue.py")
        return
    
    merchant = merchants.first()
    user = merchant.user
    
    print(f"✅ تم العثور على تاجر:")
    print(f"   البريد: {user.email}")
    print(f"   الاسم التجاري: {merchant.business_name}")
    print(f"   الحالة: '{merchant.status}'")
    print()
    
    # 2. اختبار CheckMerchantStatus
    print("[2] اختبار Check Merchant Status...")
    factory = RequestFactory()
    request = factory.get('/api/v1/merchant/check-status/')
    force_authenticate(request, user=user)
    
    view = CheckMerchantStatusView.as_view()
    response = view(request)
    
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.data}")
    
    if response.status_code == 200:
        if response.data.get('is_merchant'):
            print("   ✅ التاجر معتمد")
        else:
            print("   ❌ التاجر غير معتمد!")
    print()
    
    # 3. اختبار Create Offer
    print("[3] اختبار Create Offer...")
    
    # التأكد من وجود مدينة
    city = City.objects.first()
    if not city:
        print("   ❌ لا توجد مدن في النظام!")
        return
    
    offer_data = {
        'title': 'عرض اختبار مباشر',
        'description': 'وصف العرض الاختباري',
        'price_before': '100',
        'price_after': '50',
        'city': str(city.id),
        'status': 'مقبول'
    }
    
    request = factory.post('/api/v1/merchant/offers/create/', data=offer_data)
    force_authenticate(request, user=user)
    
    view = MerchantOfferCreateView.as_view()
    response = view(request)
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 201:
        print("   ✅ تم إنشاء العرض بنجاح!")
        print(f"   Response: {response.data}")
    elif response.status_code == 403:
        print("   ❌ 403 Forbidden - المشكلة ما زالت موجودة!")
        print(f"   Response: {response.data}")
        print()
        print("   🔍 تحليل المشكلة:")
        
        # فحص مباشر
        try:
            test_merchant = Merchant.objects.get(user=user, status='مقبول')
            print(f"   ✅ يمكن الوصول للتاجر مباشرة")
            print(f"      ID: {test_merchant.id}")
            print(f"      الحالة: '{test_merchant.status}'")
        except Merchant.DoesNotExist:
            print(f"   ❌ لا يمكن الوصول للتاجر!")
            print(f"   🔧 السبب:")
            print(f"      - الحالة الحالية: '{merchant.status}'")
            print(f"      - المطلوب: 'مقبول'")
            print(f"      - متطابقة؟ {merchant.status == 'مقبول'}")
    else:
        print(f"   ⚠️  رمز غير متوقع: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"   Response: {response.data}")
    
    print()
    print("=" * 60)
    print("✅ انتهى الاختبار!")

if __name__ == '__main__':
    try:
        test_merchant_api()
    except Exception as e:
        print(f"\n❌ حدث خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
