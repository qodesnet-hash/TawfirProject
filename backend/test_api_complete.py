#!/usr/bin/env python
"""
سكريبت اختبار شامل لـ API
Comprehensive API Testing Script
"""

import os
import sys
import django
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate
from api.merchant_views import (
    CheckMerchantStatusView,
    MerchantDashboardView,
    MerchantOfferCreateView
)
from api.models import Merchant, City, Category

User = get_user_model()

class APITester:
    def __init__(self):
        self.factory = RequestFactory()
        self.test_user = None
        self.test_merchant = None
        self.results = []
        
    def print_header(self, text):
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)
    
    def print_result(self, test_name, success, message=""):
        icon = "✅" if success else "❌"
        self.results.append((test_name, success))
        print(f"{icon} {test_name}")
        if message:
            print(f"   └─ {message}")
    
    def setup_test_data(self):
        """إنشاء بيانات اختبار"""
        self.print_header("📦 إنشاء بيانات الاختبار")
        
        try:
            # إنشاء مستخدم
            self.test_user, created = User.objects.get_or_create(
                email='test-merchant@tawfir.com',
                defaults={
                    'full_name': 'تاجر اختبار',
                    'user_type': 'merchant'
                }
            )
            if created:
                self.test_user.set_password('test123')
                self.test_user.save()
            
            self.print_result("إنشاء مستخدم اختبار", True, f"Email: {self.test_user.email}")
            
            # إنشاء تاجر
            self.test_merchant, created = Merchant.objects.get_or_create(
                user=self.test_user,
                defaults={
                    'business_name': 'متجر اختبار',
                    'status': 'مقبول',
                    'phone': '0500000000',
                    'address': 'عنوان اختباري'
                }
            )
            
            self.print_result("إنشاء تاجر", True, f"Status: {self.test_merchant.status}")
            
        except Exception as e:
            self.print_result("إعداد بيانات الاختبار", False, str(e))
            return False
        
        return True
    
    def test_check_merchant_status(self):
        """اختبار: التحقق من حالة التاجر"""
        self.print_header("🔍 اختبار: التحقق من حالة التاجر")
        
        try:
            request = self.factory.get('/api/v1/merchant/check-status/')
            force_authenticate(request, user=self.test_user)
            
            view = CheckMerchantStatusView.as_view()
            response = view(request)
            
            if response.status_code == 200:
                data = response.data
                self.print_result(
                    "API Response 200 OK", 
                    True, 
                    f"is_merchant: {data.get('is_merchant')}"
                )
                
                if data.get('is_merchant') == True:
                    self.print_result("التاجر معتمد", True)
                else:
                    self.print_result("التاجر غير معتمد", False)
            else:
                self.print_result("API Response", False, f"Status: {response.status_code}")
        
        except Exception as e:
            self.print_result("اختبار حالة التاجر", False, str(e))
    
    def test_merchant_dashboard(self):
        """اختبار: لوحة تحكم التاجر"""
        self.print_header("📊 اختبار: لوحة تحكم التاجر")
        
        try:
            request = self.factory.get('/api/v1/merchant/dashboard/')
            force_authenticate(request, user=self.test_user)
            
            view = MerchantDashboardView.as_view()
            response = view(request)
            
            if response.status_code == 200:
                data = response.data
                self.print_result("Dashboard API", True)
                
                if 'statistics' in data:
                    stats = data['statistics']
                    print(f"\n   📈 الإحصائيات:")
                    print(f"      - إجمالي العروض: {stats.get('total_offers', 0)}")
                    print(f"      - العروض النشطة: {stats.get('active_offers', 0)}")
                    print(f"      - إجمالي المشاهدات: {stats.get('total_views', 0)}")
                    print(f"      - التقييم: {stats.get('average_rating', 0):.1f}/5")
                    self.print_result("بيانات الإحصائيات", True)
                else:
                    self.print_result("بيانات الإحصائيات", False, "لا توجد إحصائيات")
            else:
                self.print_result("Dashboard API", False, f"Status: {response.status_code}")
        
        except Exception as e:
            self.print_result("اختبار لوحة التحكم", False, str(e))
    
    def test_create_offer(self):
        """اختبار: إنشاء عرض"""
        self.print_header("➕ اختبار: إنشاء عرض جديد")
        
        try:
            city = City.objects.first()
            if not city:
                self.print_result("إنشاء عرض", False, "لا توجد مدن في النظام")
                return
            
            offer_data = {
                'title': 'عرض اختباري',
                'description': 'وصف العرض الاختباري',
                'price_before': 100,
                'price_after': 50,
                'city': city.id,
                'status': 'مقبول'
            }
            
            request = self.factory.post(
                '/api/v1/merchant/offers/create/',
                data=offer_data
            )
            force_authenticate(request, user=self.test_user)
            
            view = MerchantOfferCreateView.as_view()
            response = view(request)
            
            if response.status_code == 201:
                self.print_result("إنشاء عرض", True, "تم إنشاء العرض بنجاح")
                print(f"   └─ ID: {response.data.get('id')}")
                print(f"   └─ العنوان: {response.data.get('title')}")
            elif response.status_code == 403:
                self.print_result("إنشاء عرض", False, "❌ 403 Forbidden - المشكلة ما زالت موجودة!")
            else:
                self.print_result("إنشاء عرض", False, f"Status: {response.status_code}")
        
        except Exception as e:
            self.print_result("اختبار إنشاء عرض", False, str(e))
    
    def print_summary(self):
        """طباعة ملخص النتائج"""
        self.print_header("📋 ملخص الاختبارات")
        
        total = len(self.results)
        passed = sum(1 for _, success in self.results if success)
        failed = total - passed
        
        print(f"\nإجمالي الاختبارات: {total}")
        print(f"✅ نجح: {passed}")
        print(f"❌ فشل: {failed}")
        
        if failed > 0:
            print("\n⚠️  الاختبارات الفاشلة:")
            for name, success in self.results:
                if not success:
                    print(f"   - {name}")
        
        print("\n" + "=" * 60)
        
        if failed == 0:
            print("🎉 جميع الاختبارات نجحت!")
        else:
            print("⚠️  بعض الاختبارات فشلت، يرجى المراجعة")
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("╔════════════════════════════════════════════════════════════╗")
        print("║         🧪 اختبار شامل لـ API - API Testing              ║")
        print("╚════════════════════════════════════════════════════════════╝")
        
        if not self.setup_test_data():
            print("\n❌ فشل إعداد بيانات الاختبار")
            return
        
        self.test_check_merchant_status()
        self.test_merchant_dashboard()
        self.test_create_offer()
        
        self.print_summary()

def main():
    tester = APITester()
    tester.run_all_tests()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ حدث خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
