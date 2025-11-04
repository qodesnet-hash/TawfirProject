"""
Script to apply governorate and city migration for merchants
نص برمجي لتطبيق تحديثات المحافظة والمدينة للتجار
"""

import os
import sys
import django

# Setup Django environment
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_database_connection():
    """Check if database connection is working"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ اتصال قاعدة البيانات ناجح")
        return True
    except Exception as e:
        print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
        return False

def create_migrations():
    """Create new migrations"""
    print_header("إنشاء Migrations")
    try:
        call_command('makemigrations', 'api', interactive=False)
        print("✅ تم إنشاء migrations بنجاح")
        return True
    except Exception as e:
        print(f"❌ خطأ في إنشاء migrations: {e}")
        return False

def apply_migrations():
    """Apply migrations to database"""
    print_header("تطبيق Migrations")
    try:
        call_command('migrate', 'api', interactive=False)
        print("✅ تم تطبيق migrations بنجاح")
        return True
    except Exception as e:
        print(f"❌ خطأ في تطبيق migrations: {e}")
        return False

def verify_fields():
    """Verify that new fields exist in database"""
    print_header("التحقق من الحقول الجديدة")
    
    try:
        from api.models import Merchant, MerchantRequest
        
        # Check Merchant model
        merchant_fields = [f.name for f in Merchant._meta.get_fields()]
        has_governorate = 'governorate' in merchant_fields
        has_city = 'city' in merchant_fields
        
        print(f"Merchant.governorate: {'✅ موجود' if has_governorate else '❌ غير موجود'}")
        print(f"Merchant.city: {'✅ موجود' if has_city else '❌ غير موجود'}")
        
        # Check MerchantRequest model
        request_fields = [f.name for f in MerchantRequest._meta.get_fields()]
        has_gov_request = 'governorate' in request_fields
        has_city_request = 'city' in request_fields
        
        print(f"MerchantRequest.governorate: {'✅ موجود' if has_gov_request else '❌ غير موجود'}")
        print(f"MerchantRequest.city: {'✅ موجود' if has_city_request else '❌ غير موجود'}")
        
        return has_governorate and has_city and has_gov_request and has_city_request
    except Exception as e:
        print(f"❌ خطأ في التحقق: {e}")
        return False

def main():
    """Main execution function"""
    print_header("🚀 بدء تطبيق تحديثات المحافظة والمدينة")
    
    # Step 1: Check database connection
    if not check_database_connection():
        print("\n❌ فشل الاتصال بقاعدة البيانات. تأكد من تشغيل الخادم.")
        return
    
    # Step 2: Create migrations
    if not create_migrations():
        print("\n❌ فشل إنشاء migrations.")
        return
    
    # Step 3: Apply migrations
    if not apply_migrations():
        print("\n❌ فشل تطبيق migrations.")
        return
    
    # Step 4: Verify fields
    if not verify_fields():
        print("\n⚠️  تحذير: بعض الحقول قد لا تكون موجودة.")
    
    print_header("✅ تم تطبيق جميع التحديثات بنجاح!")
    print("""
التالي:
1. أعد تشغيل الخادم: python manage.py runserver
2. افتح التطبيق: http://localhost:8100
3. جرب تسجيل تاجر جديد
4. اختر المحافظة ثم المدينة
    """)

if __name__ == '__main__':
    main()
