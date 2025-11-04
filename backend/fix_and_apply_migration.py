"""
Fix migration and create proper governorate/city fields
إصلاح الـ migration وإنشاء حقول المحافظة والمدينة بشكل صحيح
"""

import os
import sys

# Setup paths
project_path = r'C:\Users\mus_2\GitHub\TawfirProject'
os.chdir(project_path)
sys.path.insert(0, project_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
import django
django.setup()

from django.core.management import call_command

def print_step(step_num, text):
    """Print formatted step"""
    print(f"\n{'='*60}")
    print(f"  الخطوة {step_num}: {text}")
    print(f"{'='*60}\n")

def delete_custom_migration():
    """Delete manually created migration file"""
    print_step(1, "حذف migration اليدوي القديم")
    
    migration_file = os.path.join(project_path, 'api', 'migrations', '0015_add_governorate_city_to_merchant.py')
    
    if os.path.exists(migration_file):
        try:
            os.remove(migration_file)
            print(f"✅ تم حذف: {migration_file}")
        except Exception as e:
            print(f"⚠️  تحذير: {e}")
    else:
        print("ℹ️  الملف غير موجود (ربما تم حذفه مسبقاً)")

def create_migrations():
    """Create migrations automatically"""
    print_step(2, "إنشاء migrations تلقائياً")
    
    try:
        print("جاري تحليل التغييرات في Models...")
        call_command('makemigrations', 'api', interactive=False, verbosity=2)
        print("\n✅ تم إنشاء migrations بنجاح!")
        return True
    except Exception as e:
        print(f"\n❌ خطأ في إنشاء migrations: {e}")
        return False

def show_migrations():
    """Show current migrations"""
    print_step(3, "عرض جميع migrations")
    
    try:
        call_command('showmigrations', 'api')
        return True
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def apply_migrations():
    """Apply migrations"""
    print_step(4, "تطبيق migrations على قاعدة البيانات")
    
    try:
        call_command('migrate', 'api', interactive=False, verbosity=2)
        print("\n✅ تم تطبيق migrations بنجاح!")
        return True
    except Exception as e:
        print(f"\n❌ خطأ في تطبيق migrations: {e}")
        return False

def verify_changes():
    """Verify that changes were applied"""
    print_step(5, "التحقق من التغييرات")
    
    try:
        from api.models import Merchant, MerchantRequest
        from django.db import connection
        
        # Check Merchant table
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'api_merchant' 
                AND column_name IN ('governorate_id', 'city_id')
            """)
            merchant_cols = [row[0] for row in cursor.fetchall()]
        
        # Check MerchantRequest table
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'api_merchantrequest' 
                AND column_name IN ('governorate_id', 'city_id')
            """)
            request_cols = [row[0] for row in cursor.fetchall()]
        
        print("\n📊 نتائج التحقق:")
        print(f"  api_merchant.governorate_id: {'✅' if 'governorate_id' in merchant_cols else '❌'}")
        print(f"  api_merchant.city_id: {'✅' if 'city_id' in merchant_cols else '❌'}")
        print(f"  api_merchantrequest.governorate_id: {'✅' if 'governorate_id' in request_cols else '❌'}")
        print(f"  api_merchantrequest.city_id: {'✅' if 'city_id' in request_cols else '❌'}")
        
        all_ok = (
            'governorate_id' in merchant_cols and 
            'city_id' in merchant_cols and
            'governorate_id' in request_cols and 
            'city_id' in request_cols
        )
        
        return all_ok
        
    except Exception as e:
        print(f"\n⚠️  تحذير: {e}")
        return False

def main():
    """Main execution"""
    print("\n" + "🚀 " * 30)
    print("     إصلاح وتطبيق نظام المحافظة والمدينة للتجار")
    print("🚀 " * 30)
    
    # Step 1: Delete old migration
    delete_custom_migration()
    
    # Step 2: Create migrations
    if not create_migrations():
        print("\n❌ فشل. يرجى التحقق من الأخطاء أعلاه.")
        return
    
    # Step 3: Show migrations
    show_migrations()
    
    # Step 4: Apply migrations
    if not apply_migrations():
        print("\n❌ فشل. يرجى التحقق من الأخطاء أعلاه.")
        return
    
    # Step 5: Verify
    if verify_changes():
        print("\n" + "✅ " * 30)
        print("     تم تطبيق جميع التغييرات بنجاح!")
        print("✅ " * 30)
        print("""
التالي:
1. أعد تشغيل الخادم:
   python manage.py runserver

2. افتح Frontend:
   cd tawfir_app
   ionic serve

3. جرب تسجيل تاجر جديد في:
   http://localhost:8100/merchant-request
        """)
    else:
        print("\n⚠️  تحذير: بعض الحقول قد لا تكون موجودة. تحقق من الأخطاء.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  تم إيقاف العملية من قبل المستخدم.")
    except Exception as e:
        print(f"\n\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
