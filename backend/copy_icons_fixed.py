import shutil
import os
from pathlib import Path

print("="*60)
print("Copying Android Icons")
print("="*60)
print()

# المسارات
project_root = Path(r"C:\Users\mus_2\GitHub\TawfirProject")
source_base = project_root / "AppIcons" / "android"
target_base = project_root / "tawfir_app" / "android" / "app" / "src" / "main" / "res"

# المجلدات
folders = ["mipmap-hdpi", "mipmap-mdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"]

copied = 0
errors = 0

for folder in folders:
    src_folder = source_base / folder
    dst_folder = target_base / folder
    
    print(f"Processing {folder}...")
    
    # التأكد من وجود المجلد المستهدف
    try:
        dst_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"  ERROR creating folder: {e}")
        errors += 1
        continue
    
    # نسخ الأيقونة الأصلية
    src_file = src_folder / "ic_launcher.png"
    if src_file.exists():
        try:
            # نسخ ic_launcher.png
            dst_file = dst_folder / "ic_launcher.png"
            shutil.copy2(src_file, dst_file)
            print(f"  OK: {folder}/ic_launcher.png")
            copied += 1
            
            # نسخ أيضاً كـ ic_launcher_round.png
            dst_round = dst_folder / "ic_launcher_round.png"
            shutil.copy2(src_file, dst_round)
            print(f"  OK: {folder}/ic_launcher_round.png")
            copied += 1
        except Exception as e:
            print(f"  ERROR copying: {e}")
            errors += 1
    else:
        print(f"  ERROR: Source file not found!")
        errors += 1

print()
print("="*60)
print(f"Copied {copied} files successfully!")
if errors > 0:
    print(f"Errors: {errors}")
print("="*60)
print()
print("Next steps:")
print("1. cd tawfir_app")
print("2. ionic build")
print("3. npx cap sync android")
print("4. npx cap open android")
print()
print("Then in Android Studio:")
print("- Build > Clean Project")
print("- Build > Rebuild Project")
print("- Uninstall old app from phone")
print("- Run the app")
print()
input("Press Enter to exit...")
