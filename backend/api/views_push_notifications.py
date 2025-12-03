# api/views_push_notifications.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models_push_notifications import (
    NotificationPlan,
    MerchantNotificationCredit,
    NotificationPurchaseRequest,
    PushNotificationLog
)
from .models import Offer, PaymentAccount
from .models_notifications import FCMToken
from .serializers_push_notifications import (
    NotificationPlanSerializer,
    MerchantNotificationCreditSerializer,
    NotificationPurchaseRequestSerializer,
    NotificationPurchaseRequestListSerializer,
    SendNotificationSerializer,
    PushNotificationLogSerializer
)
from .fcm_service import send_push_notification


# ============= Notification Plans =============
class NotificationPlanListView(generics.ListAPIView):
    """عرض باقات الإشعارات"""
    queryset = NotificationPlan.objects.filter(is_active=True).order_by('order', 'price')
    serializer_class = NotificationPlanSerializer
    permission_classes = []


# ============= Merchant Credit =============
class MerchantNotificationCreditView(APIView):
    """عرض رصيد إشعارات التاجر"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not hasattr(request.user, 'merchant'):
            return Response({'error': 'غير مصرح'}, status=status.HTTP_403_FORBIDDEN)
        
        credit, created = MerchantNotificationCredit.objects.get_or_create(
            merchant=request.user.merchant
        )
        serializer = MerchantNotificationCreditSerializer(credit)
        return Response(serializer.data)


# ============= Purchase Requests =============
class NotificationPurchaseRequestListView(generics.ListAPIView):
    """قائمة طلبات شراء الإشعارات للتاجر"""
    serializer_class = NotificationPurchaseRequestListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'merchant'):
            return NotificationPurchaseRequest.objects.filter(
                merchant=self.request.user.merchant
            ).order_by('-created_at')
        return NotificationPurchaseRequest.objects.none()


class NotificationPurchaseRequestCreateView(generics.CreateAPIView):
    """إنشاء طلب شراء جديد"""
    serializer_class = NotificationPurchaseRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'merchant'):
            return Response(
                {'error': 'يجب أن تكون تاجراً'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NotificationPurchaseUploadReceiptView(APIView):
    """رفع إيصال الدفع"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        if not hasattr(request.user, 'merchant'):
            return Response({'error': 'غير مصرح'}, status=status.HTTP_403_FORBIDDEN)
        
        purchase_request = get_object_or_404(
            NotificationPurchaseRequest,
            pk=pk,
            merchant=request.user.merchant
        )
        
        if purchase_request.status not in ['draft', 'rejected']:
            return Response(
                {'error': 'لا يمكن رفع إيصال لهذا الطلب'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'payment_receipt' not in request.FILES:
            return Response(
                {'error': 'الرجاء رفع ملف الإيصال'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase_request.payment_receipt = request.FILES['payment_receipt']
        
        if 'transaction_number' in request.data:
            purchase_request.transaction_number = request.data['transaction_number']
        
        if 'payment_method_id' in request.data:
            payment_method = get_object_or_404(
                PaymentAccount,
                pk=request.data['payment_method_id'],
                is_active=True
            )
            purchase_request.payment_method = payment_method
        
        purchase_request.status = 'pending'
        purchase_request.save()
        
        serializer = NotificationPurchaseRequestSerializer(
            purchase_request, 
            context={'request': request}
        )
        return Response(serializer.data)


# ============= Send Notification =============
class SendOfferNotificationView(APIView):
    """إرسال إشعار لعرض"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if not hasattr(request.user, 'merchant'):
            return Response({'error': 'غير مصرح'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SendNotificationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        merchant = request.user.merchant
        offer_id = serializer.validated_data['offer_id']
        scope = serializer.validated_data['scope']
        
        # التحقق من الرصيد
        credit, created = MerchantNotificationCredit.objects.get_or_create(merchant=merchant)
        
        if not credit.can_send(scope):
            scope_name = "إشعارات المدينة" if scope == 'city' else "الإشعارات العامة"
            return Response(
                {'error': f'ليس لديك رصيد كافٍ من {scope_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # جلب العرض
        offer = get_object_or_404(Offer, pk=offer_id, merchant=merchant)
        
        # تحضير الإشعار
        title = serializer.validated_data.get('custom_title') or f"🔥 عرض جديد: {offer.title[:30]}"
        body = serializer.validated_data.get('custom_body') or f"خصم {offer.saving_percentage}% - {offer.title}"
        
        # جلب التوكنات المستهدفة
        if scope == 'city':
            # إشعار للمدينة فقط
            tokens = FCMToken.objects.filter(
                is_active=True,
                user__selected_city=merchant.city
            ).values_list('token', flat=True)
            target_city = merchant.city
        else:
            # إشعار للكل
            tokens = FCMToken.objects.filter(
                is_active=True
            ).values_list('token', flat=True)
            target_city = None
        
        tokens_list = list(tokens)
        
        if not tokens_list:
            return Response(
                {'error': 'لا يوجد مستخدمين لإرسال الإشعار لهم'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # إرسال الإشعار
        success_count = 0
        failed_count = 0
        
        for token in tokens_list:
            try:
                result = send_push_notification(
                    token=token,
                    title=title,
                    body=body,
                    data={'offer_id': str(offer.id), 'type': 'new_offer'}
                )
                if result:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
        
        # خصم من الرصيد
        credit.deduct(scope)
        
        # تسجيل الإشعار
        PushNotificationLog.objects.create(
            merchant=merchant,
            offer=offer,
            title=title,
            body=body,
            scope=scope,
            target_city=target_city,
            sent_count=len(tokens_list),
            success_count=success_count,
            failed_count=failed_count
        )
        
        # الرصيد المتبقي
        credit.refresh_from_db()
        
        return Response({
            'success': True,
            'message': f'تم إرسال الإشعار إلى {success_count} مستخدم',
            'sent_count': len(tokens_list),
            'success_count': success_count,
            'failed_count': failed_count,
            'remaining_credit': {
                'city_notifications': credit.city_notifications,
                'all_notifications': credit.all_notifications
            }
        })


# ============= Notification History =============
class MerchantNotificationHistoryView(generics.ListAPIView):
    """سجل إشعارات التاجر"""
    serializer_class = PushNotificationLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'merchant'):
            return PushNotificationLog.objects.filter(
                merchant=self.request.user.merchant
            ).order_by('-created_at')[:50]
        return PushNotificationLog.objects.none()
