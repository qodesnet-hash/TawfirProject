"""
إنشاء Adaptive Icons صحيحة مع Safe Zone
يقرأ logo.png ويضيف padding مناسب لكل حجم
"""

from PIL import Image
import os
from pathlib import Path

def create_adaptive_icon(logo_path, output_path, full_size, safe_size):
    """
    إنشاء adaptive icon مع padding صحيح
    
    Args:
        logo_path: مسار اللوجو الأصلي
        output_path: مسار الحفظ
        full_size: الحجم الكامل (108dp)
        safe_size: حجم المنطقة الآمنة (72dp)
    """
    # حساب padding
    padding = (full_size - safe_size) // 2
    
    # إنشاء canvas شفاف بالحجم الكامل
    canvas = Image.new('RGBA', (full_size, full_size), (0, 0, 0, 0))
    
    # قراءة اللوجو وتغيير حجمه
    logo = Image.open(logo_path)
    logo = logo.convert('RGBA')
    
    # تغيير حجم اللوجو للمنطقة الآمنة
    logo_resized = logo.resize((safe_size, safe_size), Image.Resampling.LANCZOS)
    
    # وضع اللوجو في المنتصف
    canvas.paste(logo_resized, (padding, padding), logo_resized)
    
    # حفظ
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, 'PNG', optimize=True)
    
    return True

def main():
    print("="*60)
    print("Creating Adaptive Icons with Safe Zone")
    print("="*60)
    print()
    
    # المسارات
    project_root = Path(r"C:\Users\mus_2\GitHub\TawfirProject")
    logo_path = project_root / "tawfir_app" / "src" / "assets" / "images" / "logo.png"
    target_base = project_root / "tawfir_app" / "android" / "app" / "src" / "main" / "res"
    
    # التحقق من وجود اللوجو
    if not logo_path.exists():
        print(f"ERROR: Logo not found at {logo_path}")
        return False
    
    print(f"Reading logo from: {logo_path}")
    print()
    
    # الأحجام (full_size, safe_size) - بالبكسل
    sizes = {
        'mipmap-mdpi': (108, 72),
        'mipmap-hdpi': (162, 108),
        'mipmap-xhdpi': (216, 144),
        'mipmap-xxhdpi': (324, 216),
        'mipmap-xxxhdpi': (432, 288)
    }
    
    created = 0
    errors = 0
    
    for folder, (full_size, safe_size) in sizes.items():
        output_folder = target_base / folder
        output_file = output_folder / "ic_launcher_foreground.png"
        
        print(f"Creating {folder}...")
        print(f"  Full size: {full_size}x{full_size}px")
        print(f"  Safe zone: {safe_size}x{safe_size}px")
        print(f"  Padding: {(full_size - safe_size) // 2}px each side")
        
        try:
            success = create_adaptive_icon(logo_path, output_file, full_size, safe_size)
            if success:
                print(f"  ✓ Created: {output_file}")
                created += 1
            else:
                print(f"  ✗ Failed")
                errors += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            errors += 1
        
        print()
    
    print("="*60)
    print(f"✓ Created {created} foreground icons")
    if errors > 0:
        print(f"✗ Errors: {errors}")
    print("="*60)
    print()
    print("Next steps:")
    print("1. cd tawfir_app")
    print("2. ionic build")
    print("3. npx cap sync android")
    print("4. In Android Studio: Build > Clean + Rebuild")
    print("5. Uninstall old app and reinstall")
    print()
    
    return True

if __name__ == "__main__":
    try:
        # التحقق من PIL
        import PIL
        print("PIL/Pillow is installed ✓")
        print()
    except ImportError:
        print("ERROR: PIL/Pillow not installed!")
        print("Please install: pip install Pillow")
        print()
        input("Press Enter to exit...")
        exit(1)
    
    success = main()
    input("Press Enter to exit...")
