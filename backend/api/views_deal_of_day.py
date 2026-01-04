from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import F

from .models import (
    DealOfDaySettings, 
    DealOfDayRequest, 
    Offer, 
    PaymentAccount
)
from .serializers import (
    DealOfDaySettingsSerializer,
    DealOfDayRequestSerializer,
    DealOfDayOfferSerializer
)


# ============= Public Views =============

class DealOfDayListView(APIView):
    """
    جلب صفقات اليوم للعرض في الواجهة
    GET /api/v1/deal-of-day/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        settings = DealOfDaySettings.get_settings()
        
        # التحقق من تفعيل الميزة
        if not settings.is_active:
            return Response({
                'deals': [],
                'mode': settings.mode,
                'message': 'صفقة اليوم غير مفعلة حالياً'
            })
        
        city_id = request.query_params.get('city_id')
        now = timezone.now()
        deals = []
        
        # جلب الصفقات المدفوعة النشطة
        paid_requests = DealOfDayRequest.objects.filter(
            status='active',
            start_date__lte=now,
            end_date__gte=now
        ).select_related('offer', 'offer__merchant', 'offer__city', 'offer__category')
        
        # فلترة حسب المدينة إن وجدت
        if city_id:
            paid_requests = paid_requests.filter(offer__city_id=city_id)
        
        # تحويل الطلبات المدفوعة إلى عروض
        paid_offers = [req.offer for req in paid_requests]
        
        if paid_offers:
            # يوجد صفقات مدفوعة
            serializer = DealOfDayOfferSerializer(
                paid_offers, 
                many=True, 
                context={'request': request}
            )
            deals = serializer.data
        elif settings.mode == 'auto':
            # الوضع التلقائي - جلب أعلى خصم
            auto_offers = Offer.objects.filter(
                status='مقبول'
            ).exclude(
                end_at__lt=now  # استبعاد المنتهية
            ).select_related(
                'merchant', 'city', 'category'
            )
            
            # فلترة حسب المدينة إن وجدت
            if city_id:
                auto_offers = auto_offers.filter(city_id=city_id)
            
            # فلترة حسب نسبة الخصم في Python
            auto_offers_list = [o for o in auto_offers if o.saving_percentage >= settings.min_discount]
            auto_offers_list = sorted(auto_offers_list, key=lambda x: (-x.saving_percentage, -x.id))[:5]
            
            if auto_offers_list:
                serializer = DealOfDayOfferSerializer(
                    auto_offers_list, 
                    many=True, 
                    context={'request': request}
                )
                deals = serializer.data
        
        return Response({
            'deals': deals,
            'mode': settings.mode,
            'count': len(deals)
        })


class DealOfDayByCityView(APIView):
    """
    جلب صفقات اليوم لمدينة محددة
    GET /api/v1/deal-of-day/city/{city_id}/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, city_id):
        settings = DealOfDaySettings.get_settings()
        
        if not settings.is_active:
            return Response({
                'deals': [],
                'mode': settings.mode,
                'message': 'صفقة اليوم غير مفعلة حالياً'
            })
        
        now = timezone.now()
        deals = []
        
        # جلب الصفقات المدفوعة النشطة للمدينة
        paid_requests = DealOfDayRequest.objects.filter(
            status='active',
            start_date__lte=now,
            end_date__gte=now,
            offer__city_id=city_id
        ).select_related('offer', 'offer__merchant', 'offer__city', 'offer__category')
        
        paid_offers = [req.offer for req in paid_requests]
        
        if paid_offers:
            serializer = DealOfDayOfferSerializer(
                paid_offers, 
                many=True, 
                context={'request': request}
            )
            deals = serializer.data
        elif settings.mode == 'auto':
            # الوضع التلقائي للمدينة
            auto_offers = Offer.objects.filter(
                status='مقبول',
                city_id=city_id
            ).exclude(
                end_at__lt=now
            ).select_related('merchant', 'city', 'category')
            
            auto_offers_list = [o for o in auto_offers if o.saving_percentage >= settings.min_discount]
            auto_offers_list = sorted(auto_offers_list, key=lambda x: (-x.saving_percentage, -x.id))[:5]
            
            if auto_offers_list:
                serializer = DealOfDayOfferSerializer(
                    auto_offers_list, 
                    many=True, 
                    context={'request': request}
                )
                deals = serializer.data
        
        return Response({
            'deals': deals,
            'mode': settings.mode,
            'city_id': city_id,
            'count': len(deals)
        })


class DealOfDaySettingsView(APIView):
    """
    جلب إعدادات صفقة اليوم (للتاجر)
    GET /api/v1/deal-of-day/settings/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        settings = DealOfDaySettings.get_settings()
        serializer = DealOfDaySettingsSerializer(settings)
        return Response(serializer.data)


class DealOfDayClickView(APIView):
    """
    تسجيل ضغطة على صفقة اليوم
    POST /api/v1/deal-of-day/{request_id}/click/
    """
    permission_classes = [AllowAny]
    
    def post(self, request, request_id):
        DealOfDayRequest.objects.filter(
            pk=request_id,
            status='active'
        ).update(clicks_count=F('clicks_count') + 1)
        
        return Response({'success': True})


# ============= Merchant Views =============

class MerchantDealOfDayRequestsView(generics.ListAPIView):
    """
    عرض قائمة طلبات صفقة اليوم للتاجر
    GET /api/v1/deal-of-day/my-requests/
    """
    serializer_class = DealOfDayRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'merchant'):
            return DealOfDayRequest.objects.filter(
                merchant=self.request.user.merchant
            ).select_related('offer', 'payment_method').order_by('-created_at')
        return DealOfDayRequest.objects.none()


class MerchantDealOfDayCreateView(generics.CreateAPIView):
    """
    إنشاء طلب صفقة اليوم جديد
    POST /api/v1/deal-of-day/create/
    """
    serializer_class = DealOfDayRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'merchant'):
            return Response(
                {'error': 'يجب أن تكون تاجراً لإنشاء طلب صفقة اليوم'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # التحقق من أن العرض يخص التاجر
        offer_id = request.data.get('offer')
        if offer_id:
            offer = get_object_or_404(Offer, pk=offer_id)
            if offer.merchant != request.user.merchant:
                return Response(
                    {'error': 'لا يمكنك إنشاء طلب لعرض لا يخصك'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # التحقق من عدم وجود طلب نشط لنفس العرض
            existing = DealOfDayRequest.objects.filter(
                offer=offer,
                status__in=['draft', 'pending', 'active']
            ).exists()
            if existing:
                return Response(
                    {'error': 'يوجد طلب قائم لهذا العرض بالفعل'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MerchantDealOfDayDetailView(generics.RetrieveAPIView):
    """
    عرض تفاصيل طلب صفقة اليوم
    GET /api/v1/deal-of-day/requests/{pk}/
    """
    serializer_class = DealOfDayRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'merchant'):
            return DealOfDayRequest.objects.filter(
                merchant=self.request.user.merchant
            ).select_related('offer', 'payment_method')
        return DealOfDayRequest.objects.none()


class MerchantDealOfDayUploadReceiptView(APIView):
    """
    رفع إيصال الدفع
    POST /api/v1/deal-of-day/requests/{pk}/upload-receipt/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if not hasattr(request.user, 'merchant'):
            return Response(
                {'error': 'غير مصرح'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        deal_request = get_object_or_404(
            DealOfDayRequest,
            pk=pk,
            merchant=request.user.merchant
        )
        
        if deal_request.status not in ['draft', 'rejected']:
            return Response(
                {'error': 'لا يمكن رفع إيصال لهذا الطلب'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'payment_receipt' not in request.FILES:
            return Response(
                {'error': 'الرجاء رفع ملف الإيصال'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deal_request.payment_receipt = request.FILES['payment_receipt']
        
        if 'transaction_number' in request.data:
            deal_request.transaction_number = request.data['transaction_number']
        
        if 'payment_method_id' in request.data:
            payment_method = get_object_or_404(
                PaymentAccount,
                pk=request.data['payment_method_id'],
                is_active=True
            )
            deal_request.payment_method = payment_method
        
        deal_request.status = 'pending'
        deal_request.save()
        
        serializer = DealOfDayRequestSerializer(deal_request, context={'request': request})
        return Response(serializer.data)


class MerchantDealOfDayStatsView(APIView):
    """
    إحصائيات صفقات اليوم للتاجر
    GET /api/v1/deal-of-day/stats/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not hasattr(request.user, 'merchant'):
            return Response({})
        
        merchant = request.user.merchant
        requests = DealOfDayRequest.objects.filter(merchant=merchant)
        
        stats = {
            'total_requests': requests.count(),
            'active_count': requests.filter(status='active').count(),
            'pending_count': requests.filter(status='pending').count(),
            'expired_count': requests.filter(status='expired').count(),
            'rejected_count': requests.filter(status='rejected').count(),
            'total_views': sum(r.views_count for r in requests),
            'total_clicks': sum(r.clicks_count for r in requests),
        }
        
        return Response(stats)
