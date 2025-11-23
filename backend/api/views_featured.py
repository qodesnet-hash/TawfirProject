from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import PaymentAccount, FeaturedPlan, FeaturedRequest, Offer
from .serializers import (
    PaymentAccountSerializer,
    FeaturedPlanSerializer,
    FeaturedRequestSerializer,
    FeaturedRequestListSerializer
)

# ============= Payment Accounts Views =============
class PaymentAccountListView(generics.ListAPIView):
    """
    عرض حسابات الدفع النشطة
    GET /api/v1/payment-accounts/
    """
    queryset = PaymentAccount.objects.filter(is_active=True).order_by('order')
    serializer_class = PaymentAccountSerializer
    permission_classes = []

# ============= Featured Plans Views =============
class FeaturedPlanListView(generics.ListAPIView):
    """
    عرض الخطط الإعلانية النشطة
    GET /api/v1/featured-plans/
    """
    queryset = FeaturedPlan.objects.filter(is_active=True).order_by('order', 'duration_days')
    serializer_class = FeaturedPlanSerializer
    permission_classes = []

# ============= Featured Requests Views =============
class FeaturedRequestListView(generics.ListAPIView):
    """
    عرض قائمة طلبات الإعلانات للتاجر
    GET /api/v1/featured-requests/
    """
    serializer_class = FeaturedRequestListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'merchant'):
            return FeaturedRequest.objects.filter(
                merchant=self.request.user.merchant
            ).select_related('plan', 'offer').order_by('-created_at')
        return FeaturedRequest.objects.none()

class FeaturedRequestCreateView(generics.CreateAPIView):
    """
    إنشاء طلب إعلان جديد
    POST /api/v1/featured-requests/create/
    """
    serializer_class = FeaturedRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'merchant'):
            return Response(
                {'error': 'يجب أن تكون تاجراً لإنشاء إعلان مميز'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FeaturedRequestDetailView(generics.RetrieveAPIView):
    """
    عرض تفاصيل طلب إعلان
    GET /api/v1/featured-requests/{id}/
    """
    serializer_class = FeaturedRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'merchant'):
            return FeaturedRequest.objects.filter(
                merchant=self.request.user.merchant
            ).select_related('plan', 'offer', 'payment_method')
        return FeaturedRequest.objects.none()

class FeaturedRequestUploadReceiptView(APIView):
    """
    رفع إيصال الدفع
    POST /api/v1/featured-requests/{id}/upload-receipt/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if not hasattr(request.user, 'merchant'):
            return Response(
                {'error': 'غير مصرح'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        featured_request = get_object_or_404(
            FeaturedRequest,
            pk=pk,
            merchant=request.user.merchant
        )
        
        if featured_request.status not in ['draft', 'rejected']:
            return Response(
                {'error': 'لا يمكن رفع إيصال لهذا الطلب'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'payment_receipt' not in request.FILES:
            return Response(
                {'error': 'الرجاء رفع ملف الإيصال'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        featured_request.payment_receipt = request.FILES['payment_receipt']
        
        if 'transaction_number' in request.data:
            featured_request.transaction_number = request.data['transaction_number']
        
        if 'payment_method_id' in request.data:
            payment_method = get_object_or_404(
                PaymentAccount,
                pk=request.data['payment_method_id'],
                is_active=True
            )
            featured_request.payment_method = payment_method
        
        featured_request.status = 'pending'
        featured_request.save()
        
        serializer = FeaturedRequestSerializer(featured_request, context={'request': request})
        return Response(serializer.data)

class MyActiveFeaturedAdsView(generics.ListAPIView):
    """
    عرض الإعلانات النشطة للتاجر
    GET /api/v1/featured-requests/my-active/
    """
    serializer_class = FeaturedRequestListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'merchant'):
            return FeaturedRequest.objects.filter(
                merchant=self.request.user.merchant,
                status='active'
            ).select_related('plan', 'offer').order_by('-start_date')
        return FeaturedRequest.objects.none()

class FeaturedRequestStatsView(APIView):
    """
    إحصائيات إعلانات التاجر
    GET /api/v1/featured-requests/stats/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not hasattr(request.user, 'merchant'):
            return Response({})
        
        merchant = request.user.merchant
        requests = FeaturedRequest.objects.filter(merchant=merchant)
        
        stats = {
            'total_requests': requests.count(),
            'active_count': requests.filter(status='active').count(),
            'pending_count': requests.filter(status='pending').count(),
            'expired_count': requests.filter(status='expired').count(),
            'rejected_count': requests.filter(status='rejected').count(),
            'total_views': sum(r.views_count for r in requests),
            'total_clicks': sum(r.clicks_count for r in requests),
            'total_favorites': sum(r.favorites_count for r in requests),
        }
        
        return Response(stats)
