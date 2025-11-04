#!/usr/bin/env python3
"""
تحديث أيقونات Android من مجلد AppIcons
يقوم بنسخ جميع الأيقونات بجميع الأحجام
"""

import os
import shutil
from pathlib import Path

def update_android_icons():
    """نسخ أيقونات Android من AppIcons إلى المجلد الصحيح"""
    
    # المسارات
    project_root = Path(__file__).parent
    source_dir = project_root / "AppIcons" / "android"
    target_dir = project_root / "tawfir_app" / "android" / "app" / "src" / "main" / "res"
    
    print("=" * 60)
    print("🔄 تحديث أيقونات Android")
    print("=" * 60)
    
    if not source_dir.exists():
        print(f"❌ مجلد المصدر غير موجود: {source_dir}")
        return False
    
    if not target_dir.exists():
        print(f"❌ مجلد الهدف غير موجود: {target_dir}")
        return False
    
    # قائمة المجلدات
    mipmap_folders = [
        "mipmap-hdpi",
        "mipmap-mdpi", 
        "mipmap-xhdpi",
        "mipmap-xxhdpi",
        "mipmap-xxxhdpi"
    ]
    
    copied_count = 0
    
    for folder in mipmap_folders:
        source_folder = source_dir / folder
        target_folder = target_dir / folder
        
        if not source_folder.exists():
            print(f"⚠️  المجلد غير موجود: {folder}")
            continue
        
        # إنشاء المجلد المستهدف إذا لم يكن موجوداً
        target_folder.mkdir(parents=True, exist_ok=True)
        
        # نسخ الأيقونة
        source_icon = source_folder / "ic_launcher.png"
        target_icon = target_folder / "ic_launcher.png"
        
        if source_icon.exists():
            # نسخ الملف
            shutil.copy2(source_icon, target_icon)
            print(f"✅ تم نسخ: {folder}/ic_launcher.png")
            copied_count += 1
            
            # نسخ أيضاً إلى ic_launcher_round.png (للأيقونات الدائرية)
            target_round = target_folder / "ic_launcher_round.png"
            shutil.copy2(source_icon, target_round)
            print(f"✅ تم نسخ: {folder}/ic_launcher_round.png")
            copied_count += 1
        else:
            print(f"⚠️  الأيقونة غير موجودة: {source_icon}")
    
    print("=" * 60)
    print(f"✅ تم نسخ {copied_count} ملف أيقونة بنجاح!")
    print("=" * 60)
    print()
    print("📱 الخطوات التالية:")
    print("1. افتح Android Studio")
    print("2. قم بعمل Clean Project: Build > Clean Project")
    print("3. أعد بناء التطبيق: Build > Rebuild Project")
    print("4. قم بتثبيت التطبيق على الجهاز")
    print()
    print("أو استخدم الأوامر:")
    print("  cd tawfir_app")
    print("  ionic build")
    print("  npx cap sync android")
    print("  npx cap open android")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = update_android_icons()
        if success:
            print("🎉 تم التحديث بنجاح!")
        else:
            print("❌ حدث خطأ أثناء التحديث")
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
