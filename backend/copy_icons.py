#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نسخ الأيقونات والشعار من مجلد AppIcons
"""

import os
import shutil
from pathlib import Path

# المسارات
BASE_DIR = Path(r"C:\Users\mus_2\GitHub\TawfirProject")
APPICONS_DIR = BASE_DIR / "AppIcons"
ANDROID_RES_DIR = BASE_DIR / "tawfir_app" / "android" / "app" / "src" / "main" / "res"
ASSETS_DIR = BASE_DIR / "tawfir_app" / "src" / "assets" / "images"

def copy_android_icons():
    """نسخ أيقونات Android"""
    print("\n[1/3] نسخ أيقونات Android...")
    print("-" * 50)
    
    mipmap_folders = [
        "mipmap-hdpi",
        "mipmap-mdpi",
        "mipmap-xhdpi",
        "mipmap-xxhdpi",
        "mipmap-xxxhdpi"
    ]
    
    for folder in mipmap_folders:
        source = APPICONS_DIR / "android" / folder
        dest = ANDROID_RES_DIR / folder
        
        if not source.exists():
            print(f"  ⚠️  {folder} غير موجود في المصدر!")
            continue
        
        # إنشاء المجلد الهدف إذا لم يكن موجوداً
        dest.mkdir(parents=True, exist_ok=True)
        
        # نسخ جميع الملفات
        files_copied = 0
        for file in source.glob("*.png"):
            dest_file = dest / file.name
            shutil.copy2(file, dest_file)
            files_copied += 1
            print(f"  ✅ {folder}/{file.name}")
        
        if files_copied == 0:
            print(f"  ⚠️  لم يتم العثور على ملفات PNG في {folder}")
    
    print("  ✅ تم نسخ جميع أيقونات Android")

def copy_logo():
    """نسخ الشعار"""
    print("\n[2/3] نسخ الشعار...")
    print("-" * 50)
    
    # إنشاء مجلد assets/images إذا لم يكن موجوداً
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    # نسخ playstore.png كـ logo.png
    playstore_png = APPICONS_DIR / "playstore.png"
    logo_png = ASSETS_DIR / "logo.png"
    
    if playstore_png.exists():
        shutil.copy2(playstore_png, logo_png)
        print(f"  ✅ logo.png (من playstore.png)")
    else:
        print(f"  ❌ playstore.png غير موجود!")
        return False
    
    # نسخ playstore.png (احتياطي)
    playstore_dest = ASSETS_DIR / "playstore.png"
    if playstore_png.exists():
        shutil.copy2(playstore_png, playstore_dest)
        print(f"  ✅ playstore.png")
    
    # نسخ appstore.png (اختياري)
    appstore_png = APPICONS_DIR / "appstore.png"
    appstore_dest = ASSETS_DIR / "appstore.png"
    if appstore_png.exists():
        shutil.copy2(appstore_png, appstore_dest)
        print(f"  ✅ appstore.png")
    
    print("  ✅ تم نسخ جميع ملفات الشعار")
    return True

def verify_files():
    """التحقق من الملفات المنسوخة"""
    print("\n[3/3] التحقق من الملفات...")
    print("-" * 50)
    
    errors = []
    
    # التحقق من أيقونات Android
    mipmap_folders = [
        "mipmap-hdpi",
        "mipmap-mdpi",
        "mipmap-xhdpi",
        "mipmap-xxhdpi",
        "mipmap-xxxhdpi"
    ]
    
    for folder in mipmap_folders:
        ic_launcher = ANDROID_RES_DIR / folder / "ic_launcher.png"
        if ic_launcher.exists():
            print(f"  ✅ {folder}/ic_launcher.png")
        else:
            errors.append(f"{folder}/ic_launcher.png غير موجود")
            print(f"  ❌ {folder}/ic_launcher.png")
    
    # التحقق من الشعار
    logo_png = ASSETS_DIR / "logo.png"
    if logo_png.exists():
        size = logo_png.stat().st_size
        print(f"  ✅ logo.png ({size // 1024} KB)")
    else:
        errors.append("logo.png غير موجود")
        print(f"  ❌ logo.png")
    
    return len(errors) == 0, errors

def main():
    print("=" * 50)
    print("  نسخ الأيقونات والشعار - Tawfir App")
    print("=" * 50)
    
    # التحقق من وجود مجلد AppIcons
    if not APPICONS_DIR.exists():
        print(f"\n❌ خطأ: مجلد AppIcons غير موجود في:")
        print(f"   {APPICONS_DIR}")
        print("\nالرجاء التأكد من وجود المجلد في المسار الصحيح.")
        return False
    
    try:
        # نسخ أيقونات Android
        copy_android_icons()
        
        # نسخ الشعار
        if not copy_logo():
            print("\n❌ فشل نسخ الشعار!")
            return False
        
        # التحقق
        success, errors = verify_files()
        
        if success:
            print("\n" + "=" * 50)
            print("✅ تم بنجاح! جميع الملفات تم نسخها")
            print("=" * 50)
            print("\n📋 الخطوة التالية:")
            print("  1. شغّل: SYNC_ICONS.bat")
            print("  2. أو شغّل: ionic cap sync android")
            print("\n🧪 للاختبار:")
            print("  cd tawfir_app")
            print("  ionic serve")
            print("=" * 50)
            return True
        else:
            print("\n⚠️ تحذير: بعض الملفات لم يتم نسخها:")
            for error in errors:
                print(f"  ❌ {error}")
            return False
            
    except Exception as e:
        print(f"\n❌ حدث خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
