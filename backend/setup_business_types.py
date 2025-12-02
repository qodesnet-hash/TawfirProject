"""
سكربت لإضافة أنواع الأنشطة التجارية الأولية
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from api.models import BusinessType

# قائمة أنواع الأنشطة
business_types = [
    {'name': 'مطاعم ومقاهي', 'icon': 'restaurant', 'order': 1},
    {'name': 'ملابس وأزياء', 'icon': 'shirt', 'order': 2},
    {'name': 'إلكترونيات', 'icon': 'phone-portrait', 'order': 3},
    {'name': 'سوبرماركت', 'icon': 'cart', 'order': 4},
    {'name': 'صيدليات', 'icon': 'medkit', 'order': 5},
    {'name': 'أثاث ومفروشات', 'icon': 'bed', 'order': 6},
    {'name': 'سيارات وقطع غيار', 'icon': 'car', 'order': 7},
    {'name': 'مجوهرات', 'icon': 'diamond', 'order': 8},
    {'name': 'خدمات (صالونات، حلاقة)', 'icon': 'cut', 'order': 9},
    {'name': 'تعليم وتدريب', 'icon': 'school', 'order': 10},
    {'name': 'صحة (عيادات، مختبرات)', 'icon': 'fitness', 'order': 11},
    {'name': 'حلويات ومخبوزات', 'icon': 'cafe', 'order': 12},
    {'name': 'أخرى', 'icon': 'ellipsis-horizontal', 'order': 99},
]

def setup_business_types():
    print("🚀 بدء إضافة أنواع الأنشطة التجارية...")
    
    created_count = 0
    updated_count = 0
    
    for bt_data in business_types:
        bt, created = BusinessType.objects.update_or_create(
            name=bt_data['name'],
            defaults={
                'icon': bt_data['icon'],
                'order': bt_data['order'],
                'is_active': True
            }
        )
        if created:
            created_count += 1
            print(f"  ✅ تم إنشاء: {bt.name}")
        else:
            updated_count += 1
            print(f"  🔄 تم تحديث: {bt.name}")
    
    print(f"\n📊 الملخص:")
    print(f"  - تم إنشاء: {created_count} نوع")
    print(f"  - تم تحديث: {updated_count} نوع")
    print(f"  - الإجمالي: {BusinessType.objects.count()} نوع")
    print("\n✅ تم الانتهاء بنجاح!")

if __name__ == '__main__':
    setup_business_types()
