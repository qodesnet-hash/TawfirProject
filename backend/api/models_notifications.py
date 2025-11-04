from django.db import models
from django.conf import settings

class FCMToken(models.Model):
    """تخزين FCM Tokens للمستخدمين"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fcm_token'
    )
    token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(
        max_length=10,
        choices=[('android', 'Android'), ('ios', 'iOS')],
        default='android'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'fcm_tokens'
        verbose_name = 'FCM Token'
        verbose_name_plural = 'FCM Tokens'

    def __str__(self):
        return f"{self.user.email} - {self.device_type}"


class Notification(models.Model):
    """سجل الإشعارات المرسلة"""
    
    NOTIFICATION_TYPES = [
        ('new_offer', 'عرض جديد'),
        ('featured_offer', 'عرض مميز'),
        ('general', 'إشعار عام'),
        ('merchant_approved', 'قبول تاجر'),
    ]
    
    title = models.CharField(max_length=100)
    body = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='general'
    )
    
    # اختياري: ربط بعرض معين
    offer = models.ForeignKey(
        'api.Offer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # للإرسال لمستخدمين محددين أو الجميع
    target_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='received_notifications'
    )
    send_to_all = models.BooleanField(default=False)
    
    # إحصائيات
    sent_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_notification_type_display()}"
