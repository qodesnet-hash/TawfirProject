"""
سكريبت لتحديث نموذج إعدادات المتواجدين بالمواضع الجديدة
"""

import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from api.models import OnlineUsersSettings

def update_model():
    """تحديث الخيارات في النموذج"""
    print("تحديث نموذج إعدادات المتواجدين...")
    
    # جلب أو إنشاء الإعدادات
    settings, created = OnlineUsersSettings.objects.get_or_create(
        pk=1,
        defaults={
            'enabled': True,
            'display_mode': 'full',
            'position': 'bottom',
            'color_scheme': 'dynamic',
            'opacity': 1.0,
            'show_activity_status': True,
            'show_mini_chart': True,
            'show_pulse_animation': True,
            'auto_hide_on_scroll': True,  # تفعيل الإخفاء عند التمرير
            'show_only_on_homepage': False,
            'update_interval': 10,
            'min_users': 25,
            'max_users': 450,
            'peak_hours_start': 18,
            'peak_hours_end': 23,
            'sound_effects': False,
            'vibration_feedback': False,
        }
    )
    
    if created:
        print("✅ تم إنشاء إعدادات جديدة")
    else:
        # تحديث الإعدادات الموجودة
        settings.auto_hide_on_scroll = True
        settings.save()
        print("✅ تم تحديث الإعدادات")
    
    print(f"""
    الإعدادات الحالية:
    - الموضع: {settings.position}
    - الإخفاء عند التمرير: {settings.auto_hide_on_scroll}
    - وضع العرض: {settings.display_mode}
    - التفعيل: {settings.enabled}
    """)

if __name__ == "__main__":
    update_model()
