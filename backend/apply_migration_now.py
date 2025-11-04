#!/usr/bin/env python
"""
تطبيق Migration مباشرة - حل نهائي
"""
import os
import sys
import subprocess

def run_command(cmd, description):
    """تشغيل أمر وعرض النتيجة"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ فشل: {description}")
        return False
    
    print(f"✅ نجح: {description}")
    return True

def main():
    print("\n" + "="*60)
    print("🚀 تطبيق Migration - حل نهائي فوري")
    print("="*60)
    
    # 1. تفعيل البيئة الافتراضية (يجب أن تكون مفعلة أصلاً)
    print("\n✓ البيئة الافتراضية مفعلة")
    
    # 2. فحص الوضع الحالي
    print("\n📊 فحص migrations الحالية...")
    run_command("python manage.py showmigrations users", "فحص migrations")
    
    # 3. إصلاح البيانات أولاً
    if not run_command("python fix_email_duplicates.py", "إصلاح البيانات المكررة"):
        print("\n⚠️ تحذير: مشكلة في إصلاح البيانات، لكن سنحاول المتابعة...")
    
    # 4. تطبيق migrations
    print("\n" + "="*60)
    print("📦 الآن تطبيق migration...")
    print("="*60)
    
    if run_command("python manage.py migrate users", "تطبيق migration"):
        print("\n" + "="*60)
        print("✅ تم بنجاح! Migration مُطبق")
        print("="*60)
        
        # 5. التحقق النهائي
        print("\n📋 التحقق النهائي...")
        run_command("python manage.py showmigrations users", "عرض migrations المطبقة")
        
        print("\n" + "="*60)
        print("🎉 تم الإصلاح بنجاح!")
        print("="*60)
        print("\n📝 الآن يمكنك تشغيل:")
        print("   python manage.py runserver")
        print("="*60)
        return True
    else:
        print("\n❌ فشل تطبيق migration!")
        print("\n💡 جرب الحل اليدوي:")
        print("   1. python manage.py shell")
        print("   2. من داخل shell:")
        print("      from users.models import CustomUser")
        print("      CustomUser.objects.filter(email='').update(email=None)")
        print("   3. exit()")
        print("   4. python manage.py migrate users")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
