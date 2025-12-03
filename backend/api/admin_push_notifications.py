# api/admin_push_notifications.py
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models_push_notifications import (
    NotificationPlan,
    MerchantNotificationCredit,
    NotificationPurchaseRequest,
    PushNotificationLog
)


@admin.register(NotificationPlan)
class NotificationPlanAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'scope', 'notifications_count', 
        'price', 'discounted_price_display', 'discount_percentage',
        'is_popular', 'is_active', 'order'
    ]
    list_filter = ['scope', 'is_active', 'is_popular']
    list_editable = ['order', 'is_active', 'is_popular']
    search_fields = ['name']
    ordering = ['order', 'price']
    
    fieldsets = (
        ('معلومات الباقة', {
            'fields': ('name', 'scope', 'notifications_count')
        }),
        ('التسعير', {
            'fields': ('price', 'discount_percentage')
        }),
        ('المميزات', {
            'fields': ('features',),
            'description': 'أدخل كل ميزة في سطر منفصل'
        }),
        ('الإعدادات', {
            'fields': ('is_popular', 'is_active', 'order')
        }),
    )
    
    def discounted_price_display(self, obj):
        if obj.discount_percentage > 0:
            return format_html(
                '<span style="text-decoration:line-through;color:#999">{}</span> '
                '<span style="color:green;font-weight:bold">{}</span>',
                f'{obj.price:,.0f}',
                f'{obj.discounted_price:,.0f}'
            )
        return f'{obj.price:,.0f}'
    discounted_price_display.short_description = 'السعر النهائي'


@admin.register(MerchantNotificationCredit)
class MerchantNotificationCreditAdmin(admin.ModelAdmin):
    list_display = [
        'merchant', 'city_notifications', 'all_notifications',
        'total_sent', 'updated_at'
    ]
    list_filter = ['updated_at']
    search_fields = ['merchant__business_name', 'merchant__user__email']
    readonly_fields = ['total_sent', 'created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return []


@admin.register(NotificationPurchaseRequest)
class NotificationPurchaseRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'merchant', 'plan', 'status_badge',
        'total_price_display', 'created_at', 'reviewed_at'
    ]
    list_filter = ['status', 'plan__scope', 'created_at']
    search_fields = ['merchant__business_name', 'merchant__user__email', 'transaction_number']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('merchant', 'plan', 'status')
        }),
        ('معلومات الدفع', {
            'fields': ('payment_method', 'payment_receipt', 'transaction_number')
        }),
        ('ملاحظات الإدارة', {
            'fields': ('admin_notes', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'reviewed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
        }
        return format_html(
            '<span style="background-color:{};color:white;padding:3px 10px;border-radius:3px">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'الحالة'
    
    def total_price_display(self, obj):
        return f'{obj.total_price:,.0f} ر.ي'
    total_price_display.short_description = 'المبلغ'
    
    @admin.action(description='✅ الموافقة على الطلبات المحددة')
    def approve_requests(self, request, queryset):
        approved = 0
        for req in queryset.filter(status='pending'):
            if req.approve():
                approved += 1
        self.message_user(request, f'تم الموافقة على {approved} طلب')
    
    @admin.action(description='❌ رفض الطلبات المحددة')
    def reject_requests(self, request, queryset):
        rejected = queryset.filter(status='pending').count()
        for req in queryset.filter(status='pending'):
            req.reject('تم الرفض من الأدمن')
        self.message_user(request, f'تم رفض {rejected} طلب')


@admin.register(PushNotificationLog)
class PushNotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title_short', 'scope', 'merchant',
        'sent_count', 'success_count', 'failed_count', 'created_at'
    ]
    list_filter = ['scope', 'created_at']
    search_fields = ['title', 'body', 'merchant__business_name']
    readonly_fields = [
        'merchant', 'offer', 'title', 'body', 'scope',
        'target_city', 'sent_count', 'success_count', 'failed_count',
        'sent_by_admin', 'created_at'
    ]
    date_hierarchy = 'created_at'
    
    def title_short(self, obj):
        return obj.title[:40] + '...' if len(obj.title) > 40 else obj.title
    title_short.short_description = 'العنوان'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
