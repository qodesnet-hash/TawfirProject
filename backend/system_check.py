#!/usr/bin/env python
"""
سكريبت شامل للتحقق من النظام بالكامل
Comprehensive System Check Script
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from api.models import Merchant, Offer, City, Category, Favorite
from users.models import CustomUser
from django.db.models import Count, Avg

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_merchants():
    print_section("📊 فحص التجار (Merchants)")
    
    merchants = Merchant.objects.all()
    print(f"\nعدد التجار الكلي: {merchants.count()}")
    
    if merchants.exists():
        print("\nتفاصيل التجار:")
        for merchant in merchants:
            print(f"\n  🏪 {merchant.business_name}")
            print(f"     - الحالة: {merchant.status}")
            print(f"     - البريد: {merchant.user.email}")
            print(f"     - الهاتف: {merchant.phone or 'غير محدد'}")
            print(f"     - عدد العروض: {merchant.offer_set.count()}")
            print(f"     - متوسط التقييم: {merchant.average_rating:.1f}")
            print(f"     - عدد التقييمات: {merchant.reviews_count}")
    else:
        print("\n⚠️  لا يوجد تجار في النظام")
    
    # إحصائيات حسب الحالة
    print("\n📈 إحصائيات حسب الحالة:")
    for status in ['قيد المراجعة', 'مقبول', 'مرفوض']:
        count = merchants.filter(status=status).count()
        print(f"  - {status}: {count}")

def check_offers():
    print_section("🎁 فحص العروض (Offers)")
    
    offers = Offer.objects.all()
    print(f"\nعدد العروض الكلي: {offers.count()}")
    
    if offers.exists():
        print("\nإحصائيات العروض:")
        
        # حسب الحالة
        print("\n📊 حسب الحالة:")
        for status in ['مقبول', 'مسودة', 'منتهي']:
            count = offers.filter(status=status).count()
            print(f"  - {status}: {count}")
        
        # حسب المدينة
        print("\n🏙️ أكثر 5 مدن عروضاً:")
        top_cities = City.objects.annotate(
            offer_count=Count('offer')
        ).order_by('-offer_count')[:5]
        
        for city in top_cities:
            print(f"  - {city.name}: {city.offer_count} عرض")
        
        # حسب التاجر
        print("\n🏆 أكثر 5 تجار عروضاً:")
        top_merchants = Merchant.objects.annotate(
            offer_count=Count('offer')
        ).order_by('-offer_count')[:5]
        
        for merchant in top_merchants:
            print(f"  - {merchant.business_name}: {merchant.offer_count} عرض")
    else:
        print("\n⚠️  لا توجد عروض في النظام")

def check_users():
    print_section("👥 فحص المستخدمين (Users)")
    
    users = CustomUser.objects.all()
    print(f"\nعدد المستخدمين الكلي: {users.count()}")
    
    # حسب النوع
    print("\n📊 حسب نوع المستخدم:")
    for user_type in ['customer', 'merchant', 'admin']:
        count = users.filter(user_type=user_type).count()
        print(f"  - {user_type}: {count}")
    
    # المستخدمون النشطون
    active_users = users.filter(is_active=True).count()
    print(f"\n✅ المستخدمون النشطون: {active_users}")
    
    # المستخدمون الموثقون
    verified_users = users.filter(is_verified=True).count()
    print(f"✅ المستخدمون الموثقون: {verified_users}")

def check_favorites():
    print_section("❤️ فحص المفضلات (Favorites)")
    
    favorites = Favorite.objects.all()
    print(f"\nعدد المفضلات الكلي: {favorites.count()}")
    
    if favorites.exists():
        # أكثر العروض إضافة للمفضلة
        print("\n⭐ أكثر 5 عروض إضافة للمفضلة:")
        top_favorites = Offer.objects.annotate(
            fav_count=Count('favorite')
        ).order_by('-fav_count')[:5]
        
        for offer in top_favorites:
            print(f"  - {offer.title}: {offer.fav_count} مرة")

def check_cities_categories():
    print_section("🏙️ المدن والفئات")
    
    cities = City.objects.all()
    categories = Category.objects.all()
    
    print(f"\nعدد المدن: {cities.count()}")
    print(f"عدد الفئات: {categories.count()}")
    
    if cities.exists():
        print("\nالمدن النشطة:")
        for city in cities.filter(is_active=True)[:10]:
            offer_count = Offer.objects.filter(city=city, status='مقبول').count()
            print(f"  - {city.name}: {offer_count} عرض")
    
    if categories.exists():
        print("\nالفئات النشطة:")
        for category in categories.filter(is_active=True):
            offer_count = Offer.objects.filter(category=category, status='مقبول').count()
            print(f"  - {category.name}: {offer_count} عرض")

def check_database_integrity():
    print_section("🔍 فحص سلامة البيانات")
    
    issues = []
    
    # التحقق من التجار بدون مستخدم
    merchants_no_user = Merchant.objects.filter(user__isnull=True).count()
    if merchants_no_user > 0:
        issues.append(f"⚠️  {merchants_no_user} تاجر بدون مستخدم")
    
    # التحقق من العروض بدون مدينة
    offers_no_city = Offer.objects.filter(city__isnull=True).count()
    if offers_no_city > 0:
        issues.append(f"⚠️  {offers_no_city} عرض بدون مدينة")
    
    # التحقق من العروض بدون تاجر
    offers_no_merchant = Offer.objects.filter(merchant__isnull=True).count()
    if offers_no_merchant > 0:
        issues.append(f"⚠️  {offers_no_merchant} عرض بدون تاجر")
    
    # التحقق من العروض بأسعار غير منطقية
    invalid_prices = Offer.objects.filter(price_after__gte=models.F('price_before')).count()
    if invalid_prices > 0:
        issues.append(f"⚠️  {invalid_prices} عرض بسعر بعد أكبر أو يساوي السعر قبل")
    
    if issues:
        print("\n❌ مشاكل محتملة:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ لا توجد مشاكل واضحة في البيانات")

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        🔍 فحص شامل لنظام Tawfir - System Check          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        check_merchants()
        check_offers()
        check_users()
        check_favorites()
        check_cities_categories()
        check_database_integrity()
        
        print_section("✅ اكتمل الفحص بنجاح")
        print("\n💡 النصائح:")
        print("  1. راجع أي مشاكل ظهرت في الفحص")
        print("  2. تأكد من تشغيل Migration إذا لزم الأمر")
        print("  3. راجع ملف error.log للأخطاء")
        
    except Exception as e:
        print(f"\n❌ حدث خطأ أثناء الفحص: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
