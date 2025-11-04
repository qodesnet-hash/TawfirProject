#!/usr/bin/env python
"""
سكريبت لإضافة مشاهدات تجريبية للعروض
"""

import os
import sys
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings_simple')
django.setup()

from api.models import Offer, Merchant
from django.db.models import F

def add_test_views():
    print("=" * 50)
    print("📊 إضافة مشاهدات تجريبية للعروض")
    print("=" * 50)
    
    # الحصول على جميع العروض
    offers = Offer.objects.all()
    
    if not offers.exists():
        print("❌ لا توجد عروض في قاعدة البيانات")
        return
    
    print(f"\n✅ تم العثور على {offers.count()} عرض")
    
    # إضافة مشاهدات عشوائية لكل عرض
    for offer in offers:
        # إضافة مشاهدات عشوائية بين 10 و 200
        random_views = random.randint(10, 200)
        offer.views_count = F('views_count') + random_views
        offer.save(update_fields=['views_count'])
        offer.refresh_from_db()
        
        print(f"  - {offer.title}: {offer.views_count} مشاهدة")
    
    print("\n✅ تمت إضافة المشاهدات بنجاح!")
    
    # عرض إحصائيات
    print("\n📈 إحصائيات المشاهدات:")
    for merchant in Merchant.objects.filter(status='مقبول'):
        total_views = sum(offer.views_count for offer in merchant.offer_set.all())
        print(f"  - {merchant.business_name}: {total_views} مشاهدة إجمالية")

if __name__ == '__main__':
    add_test_views()
    
    print("\n" + "=" * 50)
    print("💡 نصيحة: أعد تشغيل السيرفر وافتح صفحة التحليلات")
    print("=" * 50)