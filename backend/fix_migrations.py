#!/usr/bin/env python
"""
سكريبت لإصلاح مشكلة migrations وإضافة المواضع الجديدة
"""

import os
import sys

def fix_migrations():
    """إصلاح ملفات migrations"""
    
    print("=" * 60)
    print("🔧 إصلاح مشكلة Migrations")
    print("=" * 60)
    
    # 1. حذف migration الخاطئ
    bad_migration = "api/migrations/0002_update_position_choices.py"
    if os.path.exists(bad_migration):
        os.remove(bad_migration)
        print(f"✅ تم حذف الملف الخاطئ: {bad_migration}")
    
    # 2. حذف ملفات __pycache__ للتأكد
    pycache_path = "api/migrations/__pycache__"
    if os.path.exists(pycache_path):
        for file in os.listdir(pycache_path):
            if "0002_update_position_choices" in file:
                os.remove(os.path.join(pycache_path, file))
                print(f"✅ تم حذف: {file}")
    
    print("\n✅ تم إصلاح المشكلة!")
    print("\n📝 الخطوات التالية:")
    print("1. شغّل: python manage.py migrate")
    print("2. شغّل: python manage.py runserver")
    print("\n🎯 المواضع الجديدة المتاحة:")
    print("   - floating-center (عائم في الوسط)")
    print("   - floating-left (عائم يسار)")
    print("   - floating-right (عائم يمين)")

if __name__ == "__main__":
    fix_migrations()
