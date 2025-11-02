# في نهاية ملف merchant_views.py - تحديث دالة MerchantAnalyticsView

class MerchantAnalyticsView(APIView):
    """تحليلات متقدمة للتاجر"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            merchant = Merchant.objects.get(user=request.user, status='مقبول')
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'غير مصرح لك بالوصول'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # الفترة الزمنية (افتراضياً آخر 30 يوم)
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # أكثر العروض مشاهدة
        top_offers = merchant.offer_set.all().order_by('-views_count')[:5].values(
            'id', 'title', 'views_count'
        )
        
        # إجمالي المشاهدات الحالية
        total_current_views = merchant.offer_set.aggregate(
            total=Sum('views_count')
        )['total'] or 0
        
        # توزيع التقييمات
        rating_distribution = []
        for rating in range(1, 6):
            count = merchant.reviews.filter(rating=rating).count()
            rating_distribution.append({
                'rating': rating,
                'count': count
            })
        
        # نمو المشاهدات (بيانات تجريبية)
        growth_data = []
        base_views = 10  # قيمة أساسية للمشاهدات
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            # محاكاة نمو تدريجي
            daily_views = base_views + (i * 2) + (5 if i % 3 == 0 else 0)
            
            data_point = {
                'date': date.strftime('%Y-%m-%d'),
                'views': daily_views
            }
            growth_data.append(data_point)
        
        # حساب معدل النمو
        if days >= 30:
            # مشاهدات آخر 30 يوم
            recent_views = sum(d['views'] for d in growth_data[-30:])
            # مشاهدات 30 يوم السابقة (محاكاة)
            previous_views = sum(d['views'] for d in growth_data[-60:-30]) if days >= 60 else recent_views * 0.8
            
            growth_percentage = 0
            if previous_views > 0:
                growth_percentage = ((recent_views - previous_views) / previous_views) * 100
        else:
            recent_views = sum(d['views'] for d in growth_data)
            growth_percentage = 25.0  # نسبة افتراضية للنمو
        
        # إضافة المشاهدات الفعلية إلى البيانات
        current_month_views = total_current_views + recent_views
        
        data = {
            'top_offers': list(top_offers),
            'rating_distribution': rating_distribution,
            'growth_data': growth_data,
            'comparison': {
                'current_month_views': current_month_views,
                'last_month_views': int(current_month_views * 0.75),  # تقدير
                'growth_percentage': round(growth_percentage, 2)
            }
        }
        
        return Response(data)

# إضافة endpoint لتسجيل المشاهدة
class RecordOfferViewView(APIView):
    """تسجيل مشاهدة للعرض"""
    permission_classes = [AllowAny]
    
    def post(self, request, offer_id):
        try:
            offer = Offer.objects.get(id=offer_id)
            offer.views_count = F('views_count') + 1
            offer.save(update_fields=['views_count'])
            offer.refresh_from_db()
            
            return Response({
                'success': True,
                'views_count': offer.views_count
            })
        except Offer.DoesNotExist:
            return Response(
                {'error': 'العرض غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )