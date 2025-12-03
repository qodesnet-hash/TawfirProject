# api/serializers_push_notifications.py
from rest_framework import serializers
from .models_push_notifications import (
    NotificationPlan,
    MerchantNotificationCredit,
    NotificationPurchaseRequest,
    PushNotificationLog
)
from .models import PaymentAccount, Offer


class NotificationPlanSerializer(serializers.ModelSerializer):
    """سيرياليزر لباقات الإشعارات"""
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    features_list = serializers.ListField(read_only=True)
    scope_display = serializers.CharField(source='get_scope_display', read_only=True)
    
    class Meta:
        model = NotificationPlan
        fields = [
            'id',
            'name',
            'scope',
            'scope_display',
            'notifications_count',
            'price',
            'discounted_price',
            'discount_percentage',
            'features',
            'features_list',
            'is_popular',
            'is_active'
        ]


class MerchantNotificationCreditSerializer(serializers.ModelSerializer):
    """سيرياليزر لرصيد الإشعارات"""
    class Meta:
        model = MerchantNotificationCredit
        fields = [
            'city_notifications',
            'all_notifications',
            'total_sent',
            'updated_at'
        ]


class NotificationPurchaseRequestSerializer(serializers.ModelSerializer):
    """سيرياليزر لطلبات شراء الإشعارات"""
    plan = NotificationPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=NotificationPlan.objects.filter(is_active=True),
        source='plan',
        write_only=True
    )
    payment_method_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentAccount.objects.filter(is_active=True),
        source='payment_method',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = NotificationPurchaseRequest
        fields = [
            'id',
            'plan',
            'plan_id',
            'status',
            'status_display',
            'payment_receipt',
            'payment_method_id',
            'transaction_number',
            'total_price',
            'rejection_reason',
            'created_at',
            'reviewed_at'
        ]
        read_only_fields = [
            'status',
            'rejection_reason',
            'created_at',
            'reviewed_at'
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'merchant'):
            validated_data['merchant'] = request.user.merchant
            validated_data['status'] = 'draft'
        return super().create(validated_data)


class NotificationPurchaseRequestListSerializer(serializers.ModelSerializer):
    """سيرياليزر مختصر لقائمة الطلبات"""
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_scope = serializers.CharField(source='plan.get_scope_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = NotificationPurchaseRequest
        fields = [
            'id',
            'plan_name',
            'plan_scope',
            'status',
            'status_display',
            'created_at',
            'reviewed_at'
        ]


class SendNotificationSerializer(serializers.Serializer):
    """سيرياليزر لإرسال إشعار"""
    offer_id = serializers.IntegerField()
    scope = serializers.ChoiceField(choices=['city', 'all'])
    custom_title = serializers.CharField(max_length=100, required=False, allow_blank=True)
    custom_body = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_offer_id(self, value):
        request = self.context.get('request')
        if request and hasattr(request.user, 'merchant'):
            try:
                offer = Offer.objects.get(pk=value, merchant=request.user.merchant)
                return value
            except Offer.DoesNotExist:
                raise serializers.ValidationError("العرض غير موجود أو لا يعود لك")
        raise serializers.ValidationError("غير مصرح")


class PushNotificationLogSerializer(serializers.ModelSerializer):
    """سيرياليزر لسجل الإشعارات"""
    scope_display = serializers.CharField(source='get_scope_display', read_only=True)
    offer_title = serializers.CharField(source='offer.title', read_only=True, allow_null=True)
    target_city_name = serializers.CharField(source='target_city.name', read_only=True, allow_null=True)
    
    class Meta:
        model = PushNotificationLog
        fields = [
            'id',
            'title',
            'body',
            'scope',
            'scope_display',
            'offer_title',
            'target_city_name',
            'sent_count',
            'success_count',
            'failed_count',
            'created_at'
        ]
