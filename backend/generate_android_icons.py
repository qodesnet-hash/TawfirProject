#!/usr/bin/env python3
"""
Script to generate Android app icons from logo.png
Converts the toolbar logo to all required Android icon sizes
"""

import os
from PIL import Image
import shutil

# Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(PROJECT_ROOT, 'tawfir_app', 'src', 'assets', 'images', 'logo.png')
ANDROID_RES_PATH = os.path.join(PROJECT_ROOT, 'tawfir_app', 'android', 'app', 'src', 'main', 'res')

# Icon sizes for different densities
ICON_SIZES = {
    'mipmap-mdpi': 48,
    'mipmap-hdpi': 72,
    'mipmap-xhdpi': 96,
    'mipmap-xxhdpi': 144,
    'mipmap-xxxhdpi': 192
}

# Round icon sizes (slightly larger for adaptive icons)
ROUND_ICON_SIZES = {
    'mipmap-mdpi': 48,
    'mipmap-hdpi': 72,
    'mipmap-xhdpi': 96,
    'mipmap-xxhdpi': 144,
    'mipmap-xxxhdpi': 192
}

# Foreground icon sizes (for adaptive icons - should be 108dp with 18dp padding)
FOREGROUND_SIZES = {
    'mipmap-mdpi': 108,
    'mipmap-hdpi': 162,
    'mipmap-xhdpi': 216,
    'mipmap-xxhdpi': 324,
    'mipmap-xxxhdpi': 432
}

def add_padding(img, target_size):
    """Add padding to center the logo with 18dp safe zone"""
    # Calculate padding (18dp on each side out of 108dp total = 72dp content area)
    safe_zone_ratio = 72 / 108  # Content should be 72/108 of the total size
    content_size = int(target_size * safe_zone_ratio)
    
    # Resize logo to fit content area
    img.thumbnail((content_size, content_size), Image.Resampling.LANCZOS)
    
    # Create new image with transparent background
    new_img = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
    
    # Calculate position to center the logo
    x = (target_size - img.width) // 2
    y = (target_size - img.height) // 2
    
    # Paste logo onto center
    new_img.paste(img, (x, y), img if img.mode == 'RGBA' else None)
    
    return new_img

def generate_icons():
    """Generate all Android icons from logo.png"""
    
    print("🚀 Starting Android Icon Generation...")
    print(f"📁 Logo path: {LOGO_PATH}")
    print(f"📁 Android res path: {ANDROID_RES_PATH}")
    
    # Check if logo exists
    if not os.path.exists(LOGO_PATH):
        print(f"❌ Error: Logo not found at {LOGO_PATH}")
        return False
    
    # Check if Android res folder exists
    if not os.path.exists(ANDROID_RES_PATH):
        print(f"❌ Error: Android res folder not found at {ANDROID_RES_PATH}")
        return False
    
    try:
        # Open logo
        print("\n📖 Opening logo...")
        logo = Image.open(LOGO_PATH)
        
        # Convert to RGBA if needed
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        print(f"✅ Logo loaded: {logo.size[0]}x{logo.size[1]} pixels")
        
        # Generate standard launcher icons
        print("\n🎨 Generating launcher icons...")
        for density, size in ICON_SIZES.items():
            folder_path = os.path.join(ANDROID_RES_PATH, density)
            os.makedirs(folder_path, exist_ok=True)
            
            # Resize logo
            resized_logo = logo.copy()
            resized_logo.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # Save ic_launcher.png
            output_path = os.path.join(folder_path, 'ic_launcher.png')
            resized_logo.save(output_path, 'PNG')
            print(f"  ✅ {density}/ic_launcher.png ({size}x{size})")
        
        # Generate round launcher icons
        print("\n⭕ Generating round launcher icons...")
        for density, size in ROUND_ICON_SIZES.items():
            folder_path = os.path.join(ANDROID_RES_PATH, density)
            
            # Create circular icon
            resized_logo = logo.copy()
            resized_logo.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # Create circular mask
            mask = Image.new('L', (size, size), 0)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            
            # Apply mask
            circular_icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            circular_icon.paste(resized_logo, (0, 0))
            circular_icon.putalpha(mask)
            
            # Save ic_launcher_round.png
            output_path = os.path.join(folder_path, 'ic_launcher_round.png')
            circular_icon.save(output_path, 'PNG')
            print(f"  ✅ {density}/ic_launcher_round.png ({size}x{size})")
        
        # Generate foreground icons (for adaptive icons)
        print("\n🎯 Generating foreground icons (adaptive)...")
        for density, size in FOREGROUND_SIZES.items():
            folder_path = os.path.join(ANDROID_RES_PATH, density)
            
            # Create foreground with padding
            foreground_icon = add_padding(logo.copy(), size)
            
            # Save ic_launcher_foreground.png
            output_path = os.path.join(folder_path, 'ic_launcher_foreground.png')
            foreground_icon.save(output_path, 'PNG')
            print(f"  ✅ {density}/ic_launcher_foreground.png ({size}x{size})")
        
        print("\n" + "="*60)
        print("✅ SUCCESS! All Android icons generated successfully!")
        print("="*60)
        print("\n📱 Next steps:")
        print("1. Run: cd tawfir_app")
        print("2. Run: npx cap sync android")
        print("3. Build the app for Android")
        print("\n🎉 Your app icon will now match the toolbar logo!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error generating icons: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = generate_icons()
    exit(0 if success else 1)
