# api/merchant_views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Offer, Merchant, MerchantRequest, Review, Favorite, OfferImage
from .serializers import (
    MerchantRequestSerializer, 
    MerchantDashboardSerializer,
    OfferManagementSerializer
)

class CheckMerchantStatusView(APIView):
    """التحقق من حالة التاجر"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if not user.is_authenticated:
            return Response(
                {'error': 'يجب تسجيل الدخول'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            merchant_request = MerchantRequest.objects.get(user=user)
            request_status = merchant_request.status
        except MerchantRequest.DoesNotExist:
            request_status = None
        
        try:
            merchant = Merchant.objects.get(user=user)
            is_merchant = merchant.status == 'مقبول'
            merchant_id = merchant.id
        except Merchant.DoesNotExist:
            is_merchant = False
            merchant_id = None
        
        return Response({
            'is_merchant': is_merchant,
            'merchant_id': merchant_id,
            'request_status': request_status
        })

class MerchantRequestView(APIView):
    """تقديم طلب ليصبح تاجر"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if MerchantRequest.objects.filter(user=request.user).exists():
            return Response(
                {'error': 'لديك طلب مقدم بالفعل'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # التحقق من أن المدينة تنتمي للمحافظة
        governorate_id = request.data.get('governorate')
        city_id = request.data.get('city')
        
        if governorate_id and city_id:
            from .models import City
            try:
                city = City.objects.get(id=city_id, governorate_id=governorate_id)
            except City.DoesNotExist:
                return Response(
                    {'error': 'المدينة غير صحيحة أو لا تنتمي للمحافظة المختارة'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = MerchantRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {'message': 'تم تقديم طلبك بنجاح، سيتم مراجعته قريباً'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MerchantDashboardView(APIView):
    """لوحة التحكم الرئيسية للتاجر"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            merchant = Merchant.objects.get(user=request.user, status='مقبول')
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'غير مصرح لك بالوصول'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        total_offers = merchant.offer_set.count()
        active_offers = merchant.offer_set.filter(status='مقبول').count()
        total_views = merchant.offer_set.aggregate(Sum('views_count'))['views_count__sum'] or 0
        total_favorites = Favorite.objects.filter(offer__merchant=merchant).count()
        
        reviews = merchant.reviews.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_views = merchant.offer_set.filter(
            created_at__gte=thirty_days_ago
        ).aggregate(Sum('views_count'))['views_count__sum'] or 0
        
        expiring_soon = merchant.offer_set.filter(
            status='مقبول',
            end_at__lte=timezone.now() + timedelta(days=3),
            end_at__gt=timezone.now()
        ).count()
        
        # Get ALL reviews (not limited to 5)
        recent_reviews = Review.objects.filter(merchant=merchant).order_by('-created_at')
        recent_reviews_data = [{
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at,
            'user': r.user.email,
            'user_name': r.user.full_name if hasattr(r.user, 'full_name') else r.user.email.split('@')[0]
        } for r in recent_reviews]
        
        chart_data = []
        for i in range(7):
            date = timezone.now() - timedelta(days=i)
            views = merchant.offer_set.filter(
                created_at__date=date.date()
            ).aggregate(Sum('views_count'))['views_count__sum'] or 0
            chart_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'views': views
            })
        chart_data.reverse()
        
        data = {
            'merchant': {
                'id': merchant.id,
                'business_name': merchant.business_name,
                'phone': merchant.phone,
                'address': merchant.address,
                'opening_hours': merchant.opening_hours,
                'latitude': merchant.latitude,
                'longitude': merchant.longitude,
                'governorate': merchant.governorate_id,
                'city': merchant.city_id,
                'average_rating': merchant.average_rating,
                'logo': merchant.logo.url if merchant.logo else None
            },
            'statistics': {
                'total_offers': total_offers,
                'active_offers': active_offers,
                'total_views': total_views,
                'total_favorites': total_favorites,
                'average_rating': reviews['avg_rating'] or 0,
                'total_reviews': reviews['total_reviews'],
                'recent_views': recent_views,
                'expiring_soon': expiring_soon
            },
            'chart_data': chart_data,
            'recent_reviews': recent_reviews_data
        }
        
        return Response(data)

class MerchantSettingsUpdateView(APIView):
    """تحديث إعدادات المتجر"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def put(self, request):
        try:
            merchant = Merchant.objects.get(user=request.user, status='مقبول')
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'غير مصرح لك بالوصول'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        merchant.business_name = request.data.get('business_name', merchant.business_name)
        merchant.phone = request.data.get('phone', merchant.phone)
        merchant.address = request.data.get('address', merchant.address)
        merchant.opening_hours = request.data.get('opening_hours', merchant.opening_hours)
        
        if 'latitude' in request.data:
            merchant.latitude = request.data.get('latitude')
        if 'longitude' in request.data:
            merchant.longitude = request.data.get('longitude')
        if 'logo' in request.FILES:
            merchant.logo = request.FILES['logo']
        
        merchant.save()
        
        return Response({
            'message': 'تم تحديث الإعدادات بنجاح',
            'merchant': {
                'business_name': merchant.business_name,
                'phone': merchant.phone,
                'address': merchant.address,
                'opening_hours': merchant.opening_hours,
                'latitude': merchant.latitude,
                'longitude': merchant.longitude,
                'logo': merchant.logo.url if merchant.logo else None
            }
        }, status=status.HTTP_200_OK)

class MerchantOffersListView(generics.ListAPIView):
    """قائمة عروض التاجر"""
    permission_classes = [IsAuthenticated]
    serializer_class = OfferManagementSerializer
    
    def get_queryset(self):
        try:
            merchant = Merchant.objects.get(user=self.request.user, status='مقبول')
            return merchant.offer_set.all().order_by('-created_at')
        except Merchant.DoesNotExist:
            return Offer.objects.none()

class MerchantOfferCreateView(APIView):
    """إنشاء عرض جديد"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            merchant = Merchant.objects.get(user=request.user, status='مقبول')
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'غير مصرح لك بإضافة عروض'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OfferManagementSerializer(data=request.data)
        if serializer.is_valid():
            offer = serializer.save(merchant=merchant)
            
            images = request.FILES.getlist('images')
            for image in images:
                OfferImage.objects.create(offer=offer, image=image)
            
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MerchantOfferUpdateView(APIView):
    """تحديث عرض"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request, offer_id):
        try:
            merchant = Merchant.objects.get(user=request.user, status='مقبول')
            offer = Offer.objects.get(id=offer_id, merchant=merchant)
        except (Merchant.DoesNotExist, Offer.DoesNotExist):
            return Response(
                {'error': 'العرض غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = OfferManagementSerializer(offer)
        return Response(serializer.data)
    
    def put(self, request, offer_id):
        try:
            merchant = Merchant.objects.get(user=request.user, status='مقبول')
            offer = Offer.objects.get(id=offer_id, merchant=merchant)
        except (Merchant.DoesNotExist, Offer.DoesNotExist):
            return Response(
                {'error': 'العرض غير موجود أو غير مصرح لك بتعديله'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # التحقق من وجود status في البيانات
        if 'status' in request.data:
            new_status = request.data.get('status')
            print(f'🔄 Updating offer {offer_id} status from {offer.status} to {new_status}')
            
            # التحقق من أن القيمة صحيحة
            valid_statuses = ['مقبول', 'مسودة', 'منتهي']
            if new_status in valid_statuses:
                offer.status = new_status
                offer.save()
                
                # إرجاع البيانات المحدثة
                serializer = OfferManagementSerializer(offer)
                return Response({
                    'message': f'تم تحديث حالة العرض إلى {new_status}',
                    'offer': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': f'الحالة غير صحيحة. يجب أن تكون أحد القيم: {", ".join(valid_statuses)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # إذا لم يكن هناك status، استخدم الطريقة العادية
        serializer = OfferManagementSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            images = request.FILES.getlist('images')
            if images:
                offer.images.all().delete()
                for image in images:
                    OfferImage.objects.create(offer=offer, image=image)
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MerchantOfferDeleteView(APIView):
    """حذف عرض"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, offer_id):
        try:
            merchant = Merchant.objects.get(user=request.user, status='مقبول')
            offer = Offer.objects.get(id=offer_id, merchant=merchant)
            offer.delete()
            return Response(
                {'message': 'تم حذف العرض بنجاح'},
                status=status.HTTP_204_NO_CONTENT
            )
        except (Merchant.DoesNotExist, Offer.DoesNotExist):
            return Response(
                {'error': 'العرض غير موجود أو غير مصرح لك بحذفه'},
                status=status.HTTP_404_NOT_FOUND
            )

class MerchantAnalyticsView(APIView):
    """تحليلات دقيقة 100% - معدل النمو الصحيح"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            merchant = Merchant.objects.get(user=request.user, status='مقبول')
        except Merchant.DoesNotExist:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_403_FORBIDDEN)
        
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # ✅ إجمالي المشاهدات (جميع العروض)
        total_views = merchant.offer_set.aggregate(Sum('views_count'))['views_count__sum'] or 0
        
        # ✅ أفضل العروض
        top_offers = merchant.offer_set.order_by('-views_count')[:5].values(
            'id', 'title', 'views_count'
        )
        
        # ✅ توزيع التقييمات
        rating_distribution = merchant.reviews.values('rating').annotate(
            count=Count('rating')
        ).order_by('rating')
        
        # ✅ نمو المشاهدات اليومي حسب الفترة المختارة
        growth_data = []
        period_total_views = 0
        period_offers_count = 0
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            # المشاهدات للعروض المنشأة في هذا اليوم
            daily_views = merchant.offer_set.filter(
                created_at__gte=date_start,
                created_at__lt=date_end
            ).aggregate(Sum('views_count'))['views_count__sum'] or 0
            
            # عدد العروض المنشأة في هذا اليوم
            daily_offers = merchant.offer_set.filter(
                created_at__gte=date_start,
                created_at__lt=date_end
            ).count()
            
            period_total_views += daily_views
            period_offers_count += daily_offers
            
            growth_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'views': daily_views
            })
        
        # ✅ حساب معدل النمو الصحيح
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_end = current_month_start
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        # إجمالي المشاهدات الحالي
        current_month_views = merchant.offer_set.aggregate(Sum('views_count'))['views_count__sum'] or 0
        
        # مشاهدات العروض المنشأة في الشهر الماضي
        last_month_views = merchant.offer_set.filter(
            created_at__gte=last_month_start,
            created_at__lt=last_month_end
        ).aggregate(Sum('views_count'))['views_count__sum'] or 0
        
        # حساب معدل النمو: ((الحالي - الماضي) / الماضي) × 100
        growth_percentage = 0
        if last_month_views > 0:
            growth_percentage = ((current_month_views - last_month_views) / last_month_views) * 100
        elif current_month_views > 0:
            growth_percentage = 100.0  # أول شهر
        
        data = {
            'top_offers': list(top_offers),
            'rating_distribution': list(rating_distribution),
            'growth_data': growth_data,
            'comparison': {
                'current_month_views': current_month_views,
                'last_month_views': last_month_views,
                'growth_percentage': round(growth_percentage, 2)
            },
            'period_data': {
                'period_views': period_total_views,
                'period_offers': period_offers_count,
                'period_days': days
            },
            'total_offers': merchant.offer_set.count(),
            'active_offers': merchant.offer_set.filter(status='مقبول').count(),
            'total_views': total_views
        }
        
        return Response(data)
