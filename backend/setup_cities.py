# Script للتحقق من المدن الموجودة وإضافة المدن المفقودة

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from api.models import City

# إحداثيات المدن السعودية الرئيسية
SAUDI_CITIES_DATA = {
    'الرياض': {'lat': 24.7136, 'lon': 46.6753, 'active': True},
    'جدة': {'lat': 21.5433, 'lon': 39.1728, 'active': True},
    'مكة المكرمة': {'lat': 21.4225, 'lon': 39.8261, 'active': True},
    'المدينة المنورة': {'lat': 24.4672, 'lon': 39.6024, 'active': True},
    'الدمام': {'lat': 26.4207, 'lon': 50.0888, 'active': True},
    'الخبر': {'lat': 26.2172, 'lon': 50.1971, 'active': True},
    'الظهران': {'lat': 26.2361, 'lon': 50.1048, 'active': True},
    'الأحساء': {'lat': 25.3790, 'lon': 49.5878, 'active': True},
    'القطيف': {'lat': 26.5196, 'lon': 50.0115, 'active': True},
    'الطائف': {'lat': 21.2854, 'lon': 40.4168, 'active': True},
    'بريدة': {'lat': 26.3297, 'lon': 43.9750, 'active': True},
    'تبوك': {'lat': 28.3835, 'lon': 36.5662, 'active': True},
    'حائل': {'lat': 27.5114, 'lon': 41.7208, 'active': True},
    'نجران': {'lat': 17.4933, 'lon': 44.1277, 'active': True},
    'جازان': {'lat': 16.8892, 'lon': 42.5511, 'active': True},
    'عرعر': {'lat': 30.9753, 'lon': 41.0381, 'active': True},
    'الباحة': {'lat': 20.0129, 'lon': 41.4677, 'active': True},
    'ينبع': {'lat': 24.0896, 'lon': 38.0618, 'active': True},
    'أبها': {'lat': 18.2164, 'lon': 42.5053, 'active': True},
    'خميس مشيط': {'lat': 18.3060, 'lon': 42.7297, 'active': True},
}

def check_and_add_cities():
    print("🔍 التحقق من المدن في قاعدة البيانات...")
    
    # عرض المدن الموجودة
    existing_cities = City.objects.all()
    if existing_cities:
        print(f"\n✅ المدن الموجودة حالياً ({existing_cities.count()} مدينة):")
        for city in existing_cities:
            print(f"  - {city.name} (ID: {city.id})")
    else:
        print("❌ لا توجد أي مدن في قاعدة البيانات!")
    
    # إضافة المدن المفقودة
    print("\n📝 إضافة المدن السعودية الرئيسية...")
    added_count = 0
    updated_count = 0
    
    for city_name, data in SAUDI_CITIES_DATA.items():
        city, created = City.objects.get_or_create(
            name=city_name,
            defaults={
                'is_active': data['active'],
                'latitude': data['lat'],
                'longitude': data['lon']
            }
        )
        
        if created:
            print(f"  ✅ تم إضافة: {city_name}")
            added_count += 1
        else:
            # تحديث الإحداثيات إذا لم تكن موجودة
            if not city.latitude or not city.longitude:
                city.latitude = data['lat']
                city.longitude = data['lon']
                city.save()
                print(f"  📍 تم تحديث إحداثيات: {city_name}")
                updated_count += 1
            else:
                print(f"  ⏭️ موجود بالفعل: {city_name}")
    
    print(f"\n📊 النتائج:")
    print(f"  - مدن جديدة: {added_count}")
    print(f"  - مدن محدثة: {updated_count}")
    print(f"  - إجمالي المدن: {City.objects.count()}")
    
    # عرض عينة من المدن مع الإحداثيات
    print("\n🗺️ عينة من المدن مع الإحداثيات:")
    sample_cities = City.objects.filter(latitude__isnull=False)[:5]
    for city in sample_cities:
        print(f"  - {city.name}: ({city.latitude}, {city.longitude})")

if __name__ == "__main__":
    check_and_add_cities()
