import shutil
import os
from pathlib import Path

# المسارات
project_root = Path(r"C:\Users\mus_2\GitHub\TawfirProject")
source_base = project_root / "AppIcons" / "android"
target_base = project_root / "tawfir_app" / "android" / "app" / "src" / "main" / "res"

# المجلدات
folders = ["mipmap-hdpi", "mipmap-mdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"]

print("="*60)
print("🔄 نسخ أيقونات Android")
print("="*60)

copied = 0
for folder in folders:
    src_folder = source_base / folder
    dst_folder = target_base / folder
    
    # التأكد من وجود المجلد المستهدف
    dst_folder.mkdir(parents=True, exist_ok=True)
    
    # نسخ الأيقونة الأصلية
    src_file = src_folder / "ic_launcher.png"
    if src_file.exists():
        # نسخ ic_launcher.png
        dst_file = dst_folder / "ic_launcher.png"
        shutil.copy2(src_file, dst_file)
        print(f"✅ {folder}/ic_launcher.png")
        copied += 1
        
        # نسخ أيضاً كـ ic_launcher_round.png
        dst_round = dst_folder / "ic_launcher_round.png"
        shutil.copy2(src_file, dst_round)
        print(f"✅ {folder}/ic_launcher_round.png")
        copied += 1

print("="*60)
print(f"✅ تم نسخ {copied} ملف بنجاح!")
print("="*60)
print("\n📱 الخطوات التالية:")
print("1. cd tawfir_app")
print("2. ionic build")
print("3. npx cap sync android")
print("4. npx cap open android")
print("\nأو افتح Android Studio وقم بـ:")
print("- Build > Clean Project")
print("- Build > Rebuild Project")
