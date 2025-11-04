# verify_analytics.py - التحقق من صحة التحليلات
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from api.models import Merchant, Offer
from django.db.models import Sum
from django.utils import timezone

def verify_merchant_analytics(merchant_name):
    """التحقق من تحليلات التاجر"""
    
    print(f"\n{'='*80}")
    print(f"🔍 التحقق من معدل النمو لـ: {merchant_name}")
    print(f"{'='*80}\n")
    
    try:
        merchant = Merchant.objects.get(business_name__icontains=merchant_name, status='مقبول')
    except Merchant.DoesNotExist:
        print(f"❌ التاجر '{merchant_name}' غير موجود أو غير مقبول\n")
        print("📋 التجار المتاحون:")
        for m in Merchant.objects.filter(status='مقبول'):
            print(f"   - {m.business_name}")
        return
    
    print(f"✅ التاجر: {merchant.business_name}")
    print(f"   Email: {merchant.user.email if merchant.user else 'N/A'}")
    print(f"\n{'─'*80}\n")
    
    # 1. جميع العروض
    all_offers = merchant.offer_set.all().order_by('-created_at')
    print(f"📦 إجمالي العروض: {all_offers.count()}\n")
    
    if all_offers.count() == 0:
        print("⚠️ لا توجد عروض لهذا التاجر\n")
        return
    
    # عرض تفاصيل كل عرض
    total_all_views = 0
    print("تفاصيل العروض:")
    print(f"{'─'*80}")
    for i, offer in enumerate(all_offers, 1):
        print(f"{i}. {offer.title}")
        print(f"   📅 تاريخ الإنشاء: {offer.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   👁️  المشاهدات: {offer.views_count}")
        print(f"   📊 الحالة: {offer.status}")
        total_all_views += offer.views_count
        print()
    
    # 2. حساب الشهور
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = current_month_start
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    
    print(f"{'─'*80}")
    print(f"📅 الفترات الزمنية:")
    print(f"   الشهر الحالي: {current_month_start.strftime('%Y-%m-%d')} → {now.strftime('%Y-%m-%d')}")
    print(f"   الشهر الماضي: {last_month_start.strftime('%Y-%m-%d')} → {last_month_end.strftime('%Y-%m-%d')}")
    print(f"\n{'─'*80}\n")
    
    # 3. العروض في الشهر الحالي
    current_offers = all_offers.filter(created_at__gte=current_month_start)
    print(f"📈 الشهر الحالي ({current_month_start.strftime('%B %Y')}):")
    print(f"   عدد العروض المنشأة: {current_offers.count()}")
    
    if current_offers.count() > 0:
        print(f"   العروض:")
        for offer in current_offers:
            print(f"     - {offer.title}: {offer.views_count} مشاهدة")
    
    # إجمالي مشاهدات الشهر الحالي = جميع العروض
    current_month_total_views = all_offers.aggregate(Sum('views_count'))['views_count__sum'] or 0
    print(f"   💡 إجمالي المشاهدات (جميع العروض): {current_month_total_views}")
    print()
    
    # 4. العروض في الشهر الماضي
    last_month_offers = all_offers.filter(
        created_at__gte=last_month_start,
        created_at__lt=last_month_end
    )
    
    print(f"📉 الشهر الماضي ({last_month_start.strftime('%B %Y')}):")
    print(f"   عدد العروض المنشأة: {last_month_offers.count()}")
    
    if last_month_offers.count() > 0:
        print(f"   العروض:")
        for offer in last_month_offers:
            print(f"     - {offer.title}: {offer.views_count} مشاهدة")
    
    last_month_total_views = last_month_offers.aggregate(Sum('views_count'))['views_count__sum'] or 0
    print(f"   💡 إجمالي المشاهدات: {last_month_total_views}")
    print()
    
    # 5. حساب معدل النمو
    print(f"{'='*80}")
    print(f"🧮 حساب معدل النمو الشهري:")
    print(f"{'─'*80}\n")
    
    print(f"المعادلة المستخدمة:")
    print(f"معدل النمو = ((الشهر الحالي - الشهر الماضي) / الشهر الماضي) × 100\n")
    
    if last_month_total_views > 0:
        growth = ((current_month_total_views - last_month_total_views) / last_month_total_views) * 100
        
        print(f"الحساب:")
        print(f"  الشهر الحالي: {current_month_total_views} مشاهدة")
        print(f"  الشهر الماضي: {last_month_total_views} مشاهدة")
        print(f"  الفرق: {current_month_total_views - last_month_total_views} مشاهدة")
        print(f"\n  معدل النمو = (({current_month_total_views} - {last_month_total_views}) / {last_month_total_views}) × 100")
        print(f"  معدل النمو = ({current_month_total_views - last_month_total_views} / {last_month_total_views}) × 100")
        print(f"  معدل النمو = {growth:.2f}%\n")
        
        if growth > 0:
            print(f"✅ نمو إيجابي: زيادة بنسبة {growth:.2f}%")
        elif growth < 0:
            print(f"📉 نمو سالب: انخفاض بنسبة {abs(growth):.2f}%")
        else:
            print(f"➡️  لا تغيير: المشاهدات ثابتة")
            
    elif current_month_total_views > 0:
        growth = 100.0
        print(f"⚠️  لا توجد عروض في الشهر الماضي")
        print(f"  معدل النمو (افتراضي) = 100%")
    else:
        growth = 0.0
        print(f"⚠️  لا توجد مشاهدات")
        print(f"  معدل النمو = 0%")
    
    # 6. الملخص النهائي
    print(f"\n{'='*80}")
    print(f"📊 الملخص النهائي:")
    print(f"{'─'*80}")
    print(f"  التاجر: {merchant.business_name}")
    print(f"  إجمالي العروض: {all_offers.count()}")
    print(f"  إجمالي المشاهدات: {total_all_views}")
    print(f"  مشاهدات الشهر الحالي: {current_month_total_views}")
    print(f"  مشاهدات الشهر الماضي: {last_month_total_views}")
    print(f"  معدل النمو: {growth:.2f}%")
    print(f"{'='*80}\n")
    
    # 7. التحقق من API
    print(f"🔗 للتحقق من التطبيق:")
    print(f"{'─'*80}")
    print(f"1. سجل دخول بـ: {merchant.user.email}")
    print(f"2. افتح: http://localhost:8100/merchant-analytics")
    print(f"3. يجب أن ترى:")
    print(f"   - إجمالي المشاهدات: {total_all_views}")
    print(f"   - معدل النمو: {growth:.2f}%")
    print(f"\n{'='*80}\n")

# تشغيل
if __name__ == '__main__':
    verify_merchant_analytics("ماركت طيبة")
