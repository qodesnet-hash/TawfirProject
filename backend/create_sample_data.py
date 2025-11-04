# Script لإضافة بيانات تجريبية للعروض والتجار

import os
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import City, Merchant, Offer, OfferImage
from django.utils import timezone

User = get_user_model()

# بيانات تجريبية للتجار
SAMPLE_MERCHANTS = [
    {
        'name': 'مطعم البيك',
        'phone': '+966501234567',
        'address': 'شارع الملك فهد، الرياض',
        'opening_hours': '8 صباحاً - 12 منتصف الليل',
    },
    {
        'name': 'كارفور',
        'phone': '+966502345678',
        'address': 'العليا، الرياض',
        'opening_hours': '9 صباحاً - 11 مساءً',
    },
    {
        'name': 'ماكدونالدز',
        'phone': '+966503456789',
        'address': 'طريق الملك عبدالعزيز، جدة',
        'opening_hours': '24 ساعة',
    },
    {
        'name': 'بنده',
        'phone': '+966504567890',
        'address': 'حي الروضة، جدة',
        'opening_hours': '7 صباحاً - 1 صباحاً',
    },
    {
        'name': 'دانكن دونتس',
        'phone': '+966505678901',
        'address': 'الكورنيش، الدمام',
        'opening_hours': '6 صباحاً - 12 منتصف الليل',
    },
]

# بيانات تجريبية للعروض
SAMPLE_OFFERS = [
    {
        'title': 'وجبة عائلية بسعر مخفض',
        'description': 'وجبة عائلية تكفي 4 أشخاص مع مشروبات ومقبلات',
        'price_before': 150,
        'price_after': 99,
    },
    {
        'title': 'خصم 30% على المشتريات فوق 200 ريال',
        'description': 'عرض خاص على جميع المنتجات الغذائية والاستهلاكية',
        'price_before': 200,
        'price_after': 140,
    },
    {
        'title': 'اشتري واحد واحصل على الثاني مجاناً',
        'description': 'على جميع أنواع البرجر الكلاسيكي',
        'price_before': 45,
        'price_after': 22.5,
    },
    {
        'title': 'عروض نهاية الأسبوع - خصم 25%',
        'description': 'خصومات مميزة على الخضروات والفواكه الطازجة',
        'price_before': 100,
        'price_after': 75,
    },
    {
        'title': 'قهوة + دونات بـ 15 ريال فقط',
        'description': 'عرض الصباح المميز - قهوة متوسطة مع دونات من اختيارك',
        'price_before': 25,
        'price_after': 15,
    },
    {
        'title': 'بيتزا كبيرة بسعر الوسط',
        'description': 'احصل على بيتزا كبيرة بسعر البيتزا المتوسطة',
        'price_before': 65,
        'price_after': 45,
    },
    {
        'title': 'خصم 40% على الملابس الصيفية',
        'description': 'تصفيات نهاية الموسم على جميع الملابس الصيفية',
        'price_before': 250,
        'price_after': 150,
    },
    {
        'title': 'عرض الغداء - وجبة كاملة بـ 35 ريال',
        'description': 'وجبة غداء متكاملة مع المشروب والحلوى',
        'price_before': 55,
        'price_after': 35,
    },
]

def create_sample_data():
    print("🚀 بدء إنشاء البيانات التجريبية...")
    
    # التأكد من وجود المدن
    cities = City.objects.all()
    if not cities:
        print("❌ لا توجد مدن! الرجاء تشغيل setup_cities.py أولاً")
        return
    
    print(f"✅ تم العثور على {cities.count()} مدينة")
    
    # إنشاء مستخدمين تجريبيين للتجار
    merchants_created = 0
    offers_created = 0
    
    for i, merchant_data in enumerate(SAMPLE_MERCHANTS):
        # إنشاء مستخدم للتاجر
        phone = merchant_data['phone']
        user, user_created = User.objects.get_or_create(
            phone_number=phone,
            defaults={
                'is_active': True
            }
        )
        
        if user_created:
            user.set_password('123456')  # كلمة سر افتراضية
            user.save()
        
        # إنشاء التاجر
        merchant, merchant_created = Merchant.objects.get_or_create(
            user=user,
            defaults={
                'business_name': merchant_data['name'],
                'phone': phone,
                'address': merchant_data['address'],
                'opening_hours': merchant_data['opening_hours'],
                'status': 'مقبول',
                # إضافة إحداثيات عشوائية قريبة من المدينة
                'latitude': Decimal(str(24.7136 + random.uniform(-0.5, 0.5))),
                'longitude': Decimal(str(46.6753 + random.uniform(-0.5, 0.5)))
            }
        )
        
        if merchant_created:
            merchants_created += 1
            print(f"  ✅ تم إنشاء تاجر: {merchant.business_name}")
            
            # إنشاء عروض لكل تاجر
            num_offers = random.randint(2, 4)
            for j in range(num_offers):
                offer_data = random.choice(SAMPLE_OFFERS)
                city = random.choice(cities)
                
                # تحديد تاريخ انتهاء عشوائي
                end_date = None
                if random.choice([True, False]):
                    end_date = timezone.now() + timedelta(days=random.randint(1, 30))
                
                offer = Offer.objects.create(
                    merchant=merchant,
                    title=f"{offer_data['title']} - {merchant.business_name}",
                    description=offer_data['description'],
                    price_before=Decimal(str(offer_data['price_before'])),
                    price_after=Decimal(str(offer_data['price_after'])),
                    end_at=end_date,
                    city=city,
                    status='مقبول',
                    is_featured=random.choice([True, False, False]),  # 33% chance للعروض المميزة
                    views_count=random.randint(10, 500)
                )
                
                offers_created += 1
                print(f"    📦 عرض: {offer.title[:30]}...")
        else:
            print(f"  ⏭️ التاجر {merchant.business_name} موجود بالفعل")
    
    # عرض الإحصائيات
    print(f"\n📊 الإحصائيات النهائية:")
    print(f"  - عدد التجار الجدد: {merchants_created}")
    print(f"  - عدد العروض الجديدة: {offers_created}")
    print(f"  - إجمالي التجار: {Merchant.objects.count()}")
    print(f"  - إجمالي العروض: {Offer.objects.filter(status='مقبول').count()}")
    print(f"  - العروض المميزة: {Offer.objects.filter(is_featured=True).count()}")
    
    # عرض عينة من العروض
    print("\n📋 عينة من العروض المتاحة:")
    sample_offers = Offer.objects.filter(status='مقبول').select_related('merchant', 'city')[:5]
    for offer in sample_offers:
        discount = offer.saving_percentage
        print(f"  - {offer.title[:40]}... ({discount}% خصم) - {offer.city.name}")

if __name__ == "__main__":
    create_sample_data()
