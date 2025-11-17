"""
Image Processing Utilities
معالجة وضغط الصور
"""

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def compress_image(uploaded_file, max_width=800, quality=85):
    """
    ضغط الصورة وتصغير حجمها
    
    Args:
        uploaded_file: الملف المرفوع
        max_width: أقصى عرض للصورة (الافتراضي 800px)
        quality: جودة الضغط (1-100، الافتراضي 85)
    
    Returns:
        InMemoryUploadedFile: الصورة المضغوطة
    """
    try:
        # فتح الصورة
        img = Image.open(uploaded_file)
        
        # تحويل RGBA إلى RGB إذا لزم الأمر
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # تصغير الصورة إذا كانت أكبر من max_width
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # حفظ الصورة المضغوطة
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # إنشاء ملف جديد
        compressed_file = InMemoryUploadedFile(
            output,
            'ImageField',
            f"{uploaded_file.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
        
        return compressed_file
        
    except Exception as e:
        print(f'❌ Error compressing image: {e}')
        # في حالة الفشل، إرجاع الملف الأصلي
        return uploaded_file


def compress_profile_picture(uploaded_file):
    """
    ضغط صورة الملف الشخصي
    حجم أصغر للبروفايل (500px)
    """
    return compress_image(uploaded_file, max_width=500, quality=85)


def compress_merchant_logo(uploaded_file):
    """
    ضغط شعار المتجر
    حجم متوسط (600px)
    """
    return compress_image(uploaded_file, max_width=600, quality=85)


def compress_offer_image(uploaded_file):
    """
    ضغط صورة العرض
    حجم أكبر قليلاً (1000px)
    """
    return compress_image(uploaded_file, max_width=1000, quality=88)
