"""
سكريبت لتطبيق Migration وإزالة commercial_register
"""
import os
import sys
import django

# إضافة مسار المشروع
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from django.core.management import call_command

def apply_migration():
    """تطبيق Migration لإزالة commercial_register"""
    print("=" * 60)
    print("🚀 بدء تطبيق Migration...")
    print("=" * 60)
    
    try:
        # تطبيق Migration
        print("\n📦 تطبيق migration للـ api app...")
        call_command('migrate', 'api')
        
        print("\n✅ تم تطبيق Migration بنجاح!")
        print("=" * 60)
        
        # التحقق من النتيجة
        from api.models import MerchantRequest
        print("\n🔍 التحقق من Model...")
        
        # طباعة الحقول الموجودة
        fields = [f.name for f in MerchantRequest._meta.get_fields()]
        print(f"✓ الحقول الموجودة في MerchantRequest: {fields}")
        
        if 'commercial_register' in fields:
            print("❌ تحذير: commercial_register مازال موجوداً!")
        else:
            print("✅ تم حذف commercial_register بنجاح!")
        
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ أثناء تطبيق Migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = apply_migration()
    sys.exit(0 if success else 1)
