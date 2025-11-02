from django.contrib import admin
from django.utils.html import format_html
from .models_notifications import FCMToken, Notification
from .fcm_service import FCMService


@admin.register(FCMToken)
class FCMTokenAdmin(admin.ModelAdmin):
    """إدارة FCM Tokens"""
    
    list_display = ['user_email', 'device_type', 'is_active', 'updated_at']
    list_filter = ['device_type', 'is_active', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at', 'updated_at']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'البريد الإلكتروني'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """إدارة الإشعارات - يمكن للمدير إرسال إشعارات من هنا"""
    
    list_display = [
        'title',
        'notification_type',
        'send_to_all',
        'sent_status',
        'sent_at',
        'created_at'
    ]
    list_filter = ['notification_type', 'send_to_all', 'sent_at']
    search_fields = ['title', 'body']
    readonly_fields = [
        'sent_count',
        'success_count',
        'failed_count',
        'sent_at',
        'created_at'
    ]
    filter_horizontal = ['target_users']
    
    fieldsets = (
        ('معلومات الإشعار', {
            'fields': ('title', 'body', 'notification_type')
        }),
        ('الهدف', {
            'fields': ('send_to_all', 'target_users', 'offer')
        }),
        ('الإحصائيات', {
            'fields': (
                'sent_count',
                'success_count',
                'failed_count',
                'sent_at',
                'created_at'
            )
        }),
    )
    
    def sent_status(self, obj):
        """عرض حالة الإرسال بألوان"""
        if obj.sent_at:
            if obj.failed_count == 0:
                color = 'green'
                text = f'✅ تم ({obj.success_count})'
            elif obj.success_count > 0:
                color = 'orange'
                text = f'⚠️ جزئي ({obj.success_count}/{obj.sent_count})'
            else:
                color = 'red'
                text = f'❌ فشل ({obj.failed_count})'
            
            return format_html(
                '<span style="color: {};">{}</span>',
                color,
                text
            )
        return format_html('<span style="color: gray;">⏳ لم يُرسل بعد</span>')
    
    sent_status.short_description = 'حالة الإرسال'
    
    actions = ['send_notification_action']
    
    def send_notification_action(self, request, queryset):
        """إرسال الإشعارات المحددة"""
        
        sent_count = 0
        for notification in queryset:
            if notification.sent_at:
                self.message_user(
                    request,
                    f"الإشعار '{notification.title}' تم إرساله مسبقاً",
                    level='warning'
                )
                continue
            
            try:
                if notification.send_to_all:
                    result = FCMService.send_to_all_users(
                        notification.title,
                        notification.body,
                        {
                            'type': notification.notification_type,
                            'notification_id': str(notification.id)
                        }
                    )
                else:
                    users = notification.target_users.all()
                    success = 0
                    failed = 0
                    for user in users:
                        if FCMService.send_to_user(
                            user,
                            notification.title,
                            notification.body
                        ):
                            success += 1
                        else:
                            failed += 1
                    result = {
                        'total': users.count(),
                        'success': success,
                        'failed': failed
                    }
                
                # تحديث الإحصائيات
                from django.utils import timezone
                notification.sent_count = result['total']
                notification.success_count = result['success']
                notification.failed_count = result['failed']
                notification.sent_at = timezone.now()
                notification.created_by = request.user
                notification.save()
                
                sent_count += 1
                
            except Exception as e:
                self.message_user(
                    request,
                    f"خطأ في إرسال '{notification.title}': {str(e)}",
                    level='error'
                )
        
        if sent_count > 0:
            self.message_user(
                request,
                f'تم إرسال {sent_count} إشعار بنجاح',
                level='success'
            )
    
    send_notification_action.short_description = '📤 إرسال الإشعارات المحددة'
    
    def save_model(self, request, obj, form, change):
        """حفظ المدير الذي أنشأ الإشعار"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
