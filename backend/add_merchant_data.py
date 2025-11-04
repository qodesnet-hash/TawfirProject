#!/usr/bin/env python
"""
Script to add sample merchant data with ratings
"""

import os
import sys
import django
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings_simple')
django.setup()

from api.models import Merchant, Review, Offer, City
from users.models import CustomUser

def add_merchant_data():
    print("=" * 50)
    print("📝 إضافة بيانات المتاجر والتقييمات")
    print("=" * 50)
    
    # تحديث المتاجر الموجودة
    merchants = Merchant.objects.all()
    
    if merchants.count() < 5:
        # إنشاء متاجر إضافية
        merchant_data = [
            {
                'business_name': 'هايبر ماركت التوفير',
                'phone': '+966501111111',
                'address': 'شارع الملك فهد، الرياض',
                'opening_hours': '8:00 AM - 11:00 PM',
            },
            {
                'business_name': 'متجر الأسرة',
                'phone': '+966502222222',
                'address': 'حي النسيم، جدة',
                'opening_hours': '9:00 AM - 10:00 PM',
            },
            {
                'business_name': 'سوبر ماركت العائلة',
                'phone': '+966503333333',
                'address': 'شارع الأمير سلطان، الدمام',
                'opening_hours': '7:00 AM - 12:00 AM',
            },
            {
                'business_name': 'متجر الراحة',
                'phone': '+966504444444',
                'address': 'حي الروضة، مكة',
                'opening_hours': '24/7',
            },
            {
                'business_name': 'ماركت الخير',
                'phone': '+966505555555',
                'address': 'شارع الملك عبدالعزيز، المدينة',
                'opening_hours': '6:00 AM - 11:00 PM',
            }
        ]
        
        for i, data in enumerate(merchant_data):
            # إنشاء مستخدم للمتجر
            user, _ = CustomUser.objects.get_or_create(
                phone_number=f"+96650000{i+1000}"
            )
            
            merchant, created = Merchant.objects.get_or_create(
                user=user,
                defaults={
                    'business_name': data['business_name'],
                    'phone': data['phone'],
                    'address': data['address'],
                    'opening_hours': data['opening_hours'],
                    'status': 'مقبول',
                    'latitude': Decimal(str(24.7136 + random.uniform(-1, 1))),
                    'longitude': Decimal(str(46.6753 + random.uniform(-1, 1)))
                }
            )
            
            if created:
                print(f"✅ تم إنشاء متجر: {merchant.business_name}")
    
    # تحديث جميع المتاجر بالبيانات الناقصة
    all_merchants = Merchant.objects.all()
    for merchant in all_merchants:
        updated = False
        
        if not merchant.phone:
            merchant.phone = f"+96650{random.randint(100000, 999999)}"
            updated = True
        
        if not merchant.address:
            cities = ['الرياض', 'جدة', 'الدمام', 'مكة', 'المدينة']
            merchant.address = f"شارع {random.randint(1, 50)}، {random.choice(cities)}"
            updated = True
        
        if not merchant.opening_hours:
            hours = ['8:00 AM - 10:00 PM', '9:00 AM - 11:00 PM', '7:00 AM - 12:00 AM', '24/7']
            merchant.opening_hours = random.choice(hours)
            updated = True
        
        if not merchant.latitude:
            merchant.latitude = Decimal(str(24.7136 + random.uniform(-1, 1)))
            merchant.longitude = Decimal(str(46.6753 + random.uniform(-1, 1)))
            updated = True
        
        if updated:
            merchant.save()
            print(f"✅ تم تحديث متجر: {merchant.business_name}")
    
    # إضافة تقييمات تجريبية
    print("\n📝 إضافة التقييمات...")
    
    # إنشاء مستخدمين للتقييمات
    test_users = []
    for i in range(10):
        user, _ = CustomUser.objects.get_or_create(
            phone_number=f"+96650999{i:04d}"
        )
        test_users.append(user)
    
    # إضافة تقييمات لكل متجر
    for merchant in Merchant.objects.all():
        # عدد عشوائي من التقييمات لكل متجر (3-8 تقييمات)
        num_reviews = random.randint(3, 8)
        
        for i in range(num_reviews):
            user = random.choice(test_users)
            
            # تجنب التكرار
            if Review.objects.filter(user=user, merchant=merchant).exists():
                continue
            
            # تقييمات متنوعة (معظمها إيجابي)
            rating = random.choices([3, 4, 5], weights=[1, 3, 6])[0]
            
            comments = {
                5: ["ممتاز!", "خدمة رائعة", "أسعار منافسة", "متجر مميز", "أنصح بالتعامل معهم"],
                4: ["جيد جداً", "خدمة جيدة", "يستحق التجربة", "متجر جيد"],
                3: ["مقبول", "متوسط", "يحتاج تحسين"]
            }
            
            Review.objects.create(
                user=user,
                merchant=merchant,
                rating=rating,
                comment=random.choice(comments[rating])
            )
        
        print(f"✅ تم إضافة {num_reviews} تقييمات لـ {merchant.business_name}")
    
    # عرض الإحصائيات
    print("\n" + "=" * 50)
    print("📊 أفضل 5 متاجر تقييماً:")
    
    from django.db.models import Avg, Count
    top_merchants = Merchant.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(review_count__gt=0).order_by('-avg_rating', '-review_count')[:5]
    
    for i, merchant in enumerate(top_merchants, 1):
        print(f"{i}. {merchant.business_name}: ⭐ {merchant.avg_rating:.1f} ({merchant.review_count} تقييم)")
    
    print("=" * 50)

if __name__ == '__main__':
    add_merchant_data()
