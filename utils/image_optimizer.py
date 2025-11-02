"""
Image Optimization Utility
معالجة وضغط الصور تلقائياً
"""
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def optimize_image(image_field, max_size=(800, 800), quality=85, max_file_size_kb=500):
    """
    ضغط وتحسين الصور
    
    Args:
        image_field: حقل الصورة من Django
        max_size: الحد الأقصى للأبعاد (width, height)
        quality: جودة الصورة (1-100)
        max_file_size_kb: الحد الأقصى لحجم الملف بالكيلوبايت
    
    Returns:
        InMemoryUploadedFile: الصورة المحسّنة
    """
    if not image_field:
        return None
    
    try:
        # فتح الصورة
        img = Image.open(image_field)
        
        # تحويل RGBA إلى RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # تصغير الحجم مع الحفاظ على النسبة
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # حفظ الصورة في memory
        output = BytesIO()
        
        # محاولة ضغط الصورة حتى تصل للحجم المطلوب
        current_quality = quality
        while current_quality > 20:
            output.seek(0)
            output.truncate()
            
            # حفظ بصيغة JPEG
            img_format = 'JPEG'
            img.save(output, format=img_format, quality=current_quality, optimize=True)
            
            # التحقق من حجم الملف
            size_kb = output.tell() / 1024
            if size_kb <= max_file_size_kb:
                break
            
            # تقليل الجودة تدريجياً
            current_quality -= 5
        
        output.seek(0)
        
        # إنشاء ملف جديد
        optimized_image = InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image_field.name.split('.')[0]}_optimized.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
        
        return optimized_image
    
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return image_field


def validate_image_size(image_field, max_size_mb=2):
    """
    التحقق من حجم الصورة قبل الرفع
    
    Args:
        image_field: حقل الصورة
        max_size_mb: الحد الأقصى بالميجابايت
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not image_field:
        return True, None
    
    # التحقق من الحجم
    size_mb = image_field.size / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"حجم الصورة كبير جداً ({size_mb:.1f}MB). الحد الأقصى {max_size_mb}MB"
    
    # التحقق من نوع الملف
    try:
        img = Image.open(image_field)
        img.verify()
        
        # التحقق من الصيغة
        valid_formats = ['JPEG', 'JPG', 'PNG', 'WEBP']
        if img.format not in valid_formats:
            return False, f"صيغة الصورة غير مدعومة. الصيغ المدعومة: {', '.join(valid_formats)}"
        
        return True, None
    except Exception as e:
        return False, f"الملف المرفوع ليس صورة صالحة: {str(e)}"


def create_thumbnail(image_field, size=(150, 150)):
    """
    إنشاء صورة مصغرة (thumbnail)
    
    Args:
        image_field: حقل الصورة
        size: حجم الصورة المصغرة
    
    Returns:
        InMemoryUploadedFile: الصورة المصغرة
    """
    if not image_field:
        return None
    
    try:
        img = Image.open(image_field)
        
        # تحويل RGBA إلى RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # تصغير الصورة
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # حفظ في memory
        output = BytesIO()
        img.save(output, format='JPEG', quality=80, optimize=True)
        output.seek(0)
        
        # إنشاء ملف جديد
        thumbnail = InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image_field.name.split('.')[0]}_thumb.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
        
        return thumbnail
    
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return None
