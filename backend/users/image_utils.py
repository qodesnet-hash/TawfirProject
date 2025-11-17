"""
Image Processing Utilities
معالجة وضغط الصور - يستخدم نفس نظام utils.image_optimizer
"""

import sys
import logging

logger = logging.getLogger(__name__)

# استيراد من النظام الموجود
try:
    from utils.image_optimizer import optimize_image as base_optimize_image
    from utils.image_optimizer import validate_image_size
    OPTIMIZER_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ utils.image_optimizer not found, using fallback")
    OPTIMIZER_AVAILABLE = False


def compress_profile_picture(uploaded_file):
    """
    ضغط صورة الملف الشخصي
    حجم صغير للبروفايل (500px، جودة 85%)
    """
    if not OPTIMIZER_AVAILABLE:
        logger.warning("Image optimizer not available, returning original file")
        return uploaded_file
    
    logger.info('📸 Compressing profile picture...')
    
    # التحقق من الحجم أولاً
    is_valid, error_msg = validate_image_size(uploaded_file, max_size_mb=3)
    if not is_valid:
        logger.error(f'❌ Validation failed: {error_msg}')
        from django.core.exceptions import ValidationError
        raise ValidationError(error_msg)
    
    # ضغط الصورة
    return base_optimize_image(
        uploaded_file,
        max_size=(500, 500),
        quality=85,
        max_file_size_kb=150  # 150KB max للبروفايل
    )


def compress_merchant_logo(uploaded_file):
    """
    ضغط شعار المتجر
    حجم متوسط مع جودة عالية (600px، جودة 90%)
    """
    if not OPTIMIZER_AVAILABLE:
        logger.warning("Image optimizer not available, returning original file")
        return uploaded_file
    
    logger.info('🏪 Compressing merchant logo...')
    
    is_valid, error_msg = validate_image_size(uploaded_file, max_size_mb=3)
    if not is_valid:
        logger.error(f'❌ Validation failed: {error_msg}')
        from django.core.exceptions import ValidationError
        raise ValidationError(error_msg)
    
    return base_optimize_image(
        uploaded_file,
        max_size=(600, 600),
        quality=90,
        max_file_size_kb=250  # 250KB max للشعار
    )


def compress_offer_image(uploaded_file):
    """
    ضغط صورة العرض
    حجم أكبر للعروض (1000px، جودة 88%)
    """
    if not OPTIMIZER_AVAILABLE:
        logger.warning("Image optimizer not available, returning original file")
        return uploaded_file
    
    logger.info('🎁 Compressing offer image...')
    
    is_valid, error_msg = validate_image_size(uploaded_file, max_size_mb=5)
    if not is_valid:
        logger.error(f'❌ Validation failed: {error_msg}')
        from django.core.exceptions import ValidationError
        raise ValidationError(error_msg)
    
    return base_optimize_image(
        uploaded_file,
        max_size=(1000, 1000),
        quality=88,
        max_file_size_kb=400  # 400KB max للعروض
    )


def compress_city_image(uploaded_file):
    """
    ضغط صورة المدينة/المحافظة
    حجم متوسط (800px، جودة 85%)
    """
    if not OPTIMIZER_AVAILABLE:
        logger.warning("Image optimizer not available, returning original file")
        return uploaded_file
    
    logger.info('🏙️ Compressing city/governorate image...')
    
    is_valid, error_msg = validate_image_size(uploaded_file, max_size_mb=3)
    if not is_valid:
        logger.error(f'❌ Validation failed: {error_msg}')
        from django.core.exceptions import ValidationError
        raise ValidationError(error_msg)
    
    return base_optimize_image(
        uploaded_file,
        max_size=(800, 800),
        quality=85,
        max_file_size_kb=300  # 300KB max
    )


# Re-export من النظام الأساسي
if OPTIMIZER_AVAILABLE:
    __all__ = [
        'compress_profile_picture',
        'compress_merchant_logo', 
        'compress_offer_image',
        'compress_city_image',
        'validate_image_size'
    ]
