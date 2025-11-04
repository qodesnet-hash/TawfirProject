# check_merchant_growth.py
import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from api.models import Merchant, Offer
from django.db.models import Sum
from django.utils import timezone

# البحث عن التاجر
merchant_name = "ماركت طيبة"
print(f"\n{'='*60}")
print(f"🔍 البحث عن التاجر: {merchant_name}")
print(f"{'='*60}\n")

try:
    merchant = Merchant.objects.get(business_name__icontains=merchant_name)
    print(f"✅ تم العثور على التاجر:")
    print(f"   - الاسم: {merchant.business_name}")
    print(f"   - ID: {merchant.id}")
    print(f"   - الحالة: {merchant.status}")
    print(f"\n{'='*60}\n")
    
    # عرض جميع العروض
    offers = merchant.offer_set.all()
    print(f"📦 إجمالي العروض: {offers.count()}")
    print(f"\nتفاصيل العروض:")
    print(f"{'─'*60}")
    
    total_views_all = 0
    for i, offer in enumerate(offers, 1):
        print(f"\n{i}. {offer.title}")
        print(f"   - تاريخ الإنشاء: {offer.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   - عدد المشاهدات: {offer.views_count}")
        print(f"   - الحالة: {offer.status}")
        total_views_all += offer.views_count
    
    print(f"\n{'='*60}")
    print(f"📊 إجمالي المشاهدات لجميع العروض: {total_views_all}")
    print(f"{'='*60}\n")
    
    # حساب الشهر الحالي والماضي
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = current_month_start
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    
    print(f"📅 الفترات الزمنية:")
    print(f"{'─'*60}")
    print(f"الشهر الحالي: من {current_month_start.strftime('%Y-%m-%d')} إلى {now.strftime('%Y-%m-%d')}")
    print(f"الشهر الماضي: من {last_month_start.strftime('%Y-%m-%d')} إلى {last_month_end.strftime('%Y-%m-%d')}")
    print(f"\n{'='*60}\n")
    
    # حساب مشاهدات الشهر الحالي (جميع العروض)
    current_month_views = merchant.offer_set.aggregate(
        Sum('views_count')
    )['views_count__sum'] or 0
    
    print(f"📈 مشاهدات الشهر الحالي:")
    print(f"{'─'*60}")
    print(f"الطريقة المستخدمة: إجمالي مشاهدات جميع العروض")
    print(f"النتيجة: {current_month_views} مشاهدة")
    
    # حساب مشاهدات الشهر الماضي (العروض المنشأة في الشهر الماضي)
    last_month_offers = merchant.offer_set.filter(
        created_at__gte=last_month_start,
        created_at__lt=last_month_end
    )
    
    print(f"\n📉 مشاهدات الشهر الماضي:")
    print(f"{'─'*60}")
    print(f"عدد العروض المنشأة في الشهر الماضي: {last_month_offers.count()}")
    
    if last_month_offers.count() > 0:
        print(f"\nالعروض المنشأة في الشهر الماضي:")
        for offer in last_month_offers:
            print(f"  - {offer.title}: {offer.views_count} مشاهدة (أنشئ في {offer.created_at.strftime('%Y-%m-%d')})")
    
    last_month_views = last_month_offers.aggregate(
        Sum('views_count')
    )['views_count__sum'] or 0
    
    print(f"\nالنتيجة: {last_month_views} مشاهدة")
    
    # حساب معدل النمو
    print(f"\n{'='*60}")
    print(f"🧮 حساب معدل النمو:")
    print(f"{'─'*60}")
    
    if last_month_views > 0:
        growth_percentage = ((current_month_views - last_month_views) / last_month_views) * 100
        print(f"\nالمعادلة:")
        print(f"معدل النمو = ((الشهر الحالي - الشهر الماضي) / الشهر الماضي) × 100")
        print(f"معدل النمو = (({current_month_views} - {last_month_views}) / {last_month_views}) × 100")
        print(f"معدل النمو = ({current_month_views - last_month_views} / {last_month_views}) × 100")
        print(f"معدل النمو = {(current_month_views - last_month_views) / last_month_views} × 100")
        print(f"معدل النمو = {growth_percentage:.2f}%")
        
        if growth_percentage > 0:
            print(f"\n✅ نمو إيجابي: المشاهدات زادت بنسبة {growth_percentage:.2f}%")
        elif growth_percentage < 0:
            print(f"\n❌ نمو سالب: المشاهدات انخفضت بنسبة {abs(growth_percentage):.2f}%")
        else:
            print(f"\n➡️ لا تغيير: المشاهدات ثابتة")
            
    elif current_month_views > 0:
        growth_percentage = 100.0
        print(f"\n⚠️ لا توجد عروض في الشهر الماضي")
        print(f"معدل النمو (افتراضي) = 100%")
        print(f"\n✅ هذا التاجر جديد أو لم ينشئ عروض في الشهر الماضي")
    else:
        growth_percentage = 0
        print(f"\n⚠️ لا توجد مشاهدات في كلا الشهرين")
        print(f"معدل النمو = 0%")
    
    print(f"\n{'='*60}")
    print(f"📊 الملخص النهائي:")
    print(f"{'─'*60}")
    print(f"التاجر: {merchant.business_name}")
    print(f"إجمالي العروض: {offers.count()}")
    print(f"إجمالي المشاهدات (كل العروض): {total_views_all}")
    print(f"مشاهدات الشهر الحالي: {current_month_views}")
    print(f"مشاهدات الشهر الماضي: {last_month_views}")
    print(f"معدل النمو: {growth_percentage:.2f}%")
    print(f"{'='*60}\n")
    
    # التحقق من API
    print(f"{'='*60}")
    print(f"🔗 للتحقق من API:")
    print(f"{'─'*60}")
    print(f"قم بتسجيل الدخول كـ: {merchant.user.email}")
    print(f"ثم افتح: http://localhost:8100/merchant-analytics")
    print(f"\nيجب أن ترى:")
    print(f"  - إجمالي المشاهدات: {total_views_all}")
    print(f"  - معدل النمو: {growth_percentage:.2f}%")
    print(f"{'='*60}\n")
    
except Merchant.DoesNotExist:
    print(f"❌ لم يتم العثور على التاجر: {merchant_name}")
    print(f"\n📋 التجار المتاحون:")
    print(f"{'─'*60}")
    merchants = Merchant.objects.filter(status='مقبول')
    if merchants.exists():
        for m in merchants:
            print(f"  - {m.business_name} (ID: {m.id})")
    else:
        print(f"  لا يوجد تجار مقبولون في النظام")
    print(f"\n{'='*60}\n")

except Exception as e:
    print(f"❌ خطأ: {str(e)}")
    import traceback
    traceback.print_exc()
