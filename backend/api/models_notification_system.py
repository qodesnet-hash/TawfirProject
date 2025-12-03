# api/models_notification_system.py
"""
نظام إشعارات التجار - Merchant Notification System
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator


# ============= Notification Plans =============
class NotificationPlan(models.Model):
    """باقات الإشعارات"""
    
    SCOPE_CHOICES = [
        ('city', 'مدينة التاجر'),
        ('all', 'جميع المستخدمين'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="اسم الباقة")
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, default='city', verbose_name="نطاق الإشعار")
    notifications_count = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="عدد الإشعارات")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر (ريال يمني)")
    discount_percentage = models.IntegerField(default=0, verbose_name="نسبة الخصم %")
    features = models.TextField(blank=True, null=True, verbose_name="الميزات", help_text="كل ميزة في سطر")
    is_popular = models.BooleanField(default=False, verbose_name="الأكثر طلباً")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "باقة إشعارات"
        verbose_name_plural = "باقات الإشعارات"
        ordering = ['order', 'price']
    
    def __str__(self):
        return f"{self.name} - {self.notifications_count} إشعار"
    
    @property
    def discounted_price(self):
        if self.discount_percentage > 0:
            discount = (self.price * self.discount_percentage) / 100
            return self.price - discount
        return self.price
    
    @property
    def features_list(self):
        if self.features:
            return [f.strip() for f in self.features.split('\n') if f.strip()]
        return []
    
    @property
    def scope_display(self):
        return dict(self.SCOPE_CHOICES).get(self.scope, self.scope)


# ============= Merchant Notification Credit =============
class MerchantNotificationCredit(models.Model):
    """رصيد إشعارات التاجر"""
    
    merchant = models.OneToOneField(
        'api.Merchant',
        on_delete=models.CASCADE,
        related_name='notification_credit',
        verbose_name="التاجر"
    )
    city_notifications = models.IntegerField(default=0, verbose_name="إشعارات المدينة")
    all_notifications = models.IntegerField(default=0, verbose_name="إشعارات عامة")
    total_sent = models.IntegerField(default=0, verbose_name="إجمالي المرسل")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "رصيد إشعارات تاجر"
        verbose_name_plural = "أرصدة إشعارات التجار"
    
    def __str__(self):
        return f"{self.merchant.business_name} - محلي: {self.city_notifications}, عام: {self.all_notifications}"
    
    def add_credit(self, scope, count):
        """إضافة رصيد"""
        if scope == 'city':
            self.city_notifications += count
        elif scope == 'all':
            self.all_notifications += count
        self.save()
    
    def use_credit(self, scope):
        """استخدام رصيد"""
        if scope == 'city' and self.city_notifications > 0:
            self.city_notifications -= 1
            self.total_sent += 1
            self.save()
            return True
        elif scope == 'all' and self.all_notifications > 0:
            self.all_notifications -= 1
            self.total_sent += 1
            self.save()
            return True
        return False
    
    def has_credit(self, scope):
        """التحقق من وجود رصيد"""
        if scope == 'city':
            return self.city_notifications > 0
        elif scope == 'all':
            return self.all_notifications > 0
        return False


# ============= Notification Purchase Request =============
class NotificationPurchaseRequest(models.Model):
    """طلبات شراء الإشعارات"""
    
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('pending', 'قيد المراجعة'),
        ('approved', 'موافق عليه'),
        ('rejected', 'مرفوض'),
    ]
    
    merchant = models.ForeignKey(
        'api.Merchant',
        on_delete=models.CASCADE,
        related_name='notification_purchases',
        verbose_name="التاجر"
    )
    plan = models.ForeignKey(
        NotificationPlan,
        on_delete=models.PROTECT,
        verbose_name="الباقة"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")
    
    # معلومات الدفع
    payment_receipt = models.FileField(upload_to='notification_receipts/', null=True, blank=True, verbose_name="إيصال الدفع")
    payment_method = models.ForeignKey(
        'api.PaymentAccount',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="طريقة الدفع"
    )
    transaction_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم الحوالة")
    
    # ملاحظات
    admin_notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات الإدارة")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="سبب الرفض")
    
    # تواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المراجعة")
    
    class Meta:
        verbose_name = "طلب شراء إشعارات"
        verbose_name_plural = "طلبات شراء الإشعارات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.merchant.business_name} - {self.plan.name} ({self.get_status_display()})"
    
    @property
    def total_price(self):
        return self.plan.discounted_price
    
    def approve(self):
        """الموافقة على الطلب وإضافة الرصيد"""
        if self.status == 'pending':
            self.status = 'approved'
            self.reviewed_at = timezone.now()
            self.save()
            
            # إضافة الرصيد للتاجر
            credit, created = MerchantNotificationCredit.objects.get_or_create(
                merchant=self.merchant
            )
            credit.add_credit(self.plan.scope, self.plan.notifications_count)
            
            return True
        return False
    
    def reject(self, reason=None):
        """رفض الطلب"""
        if self.status == 'pending':
            self.status = 'rejected'
            self.rejection_reason = reason
            self.reviewed_at = timezone.now()
            self.save()
            return True
        return False


# ============= Merchant Notification Log =============
class MerchantNotificationLog(models.Model):
    """سجل الإشعارات المرسلة من التجار"""
    
    SCOPE_CHOICES = [
        ('city', 'مدينة التاجر'),
        ('all', 'جميع المستخدمين'),
    ]
    
    merchant = models.ForeignKey(
        'api.Merchant',
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name="التاجر"
    )
    offer = models.ForeignKey(
        'api.Offer',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='merchant_notifications',
        verbose_name="العرض"
    )
    
    title = models.CharField(max_length=100, verbose_name="عنوان الإشعار")
    body = models.TextField(verbose_name="محتوى الإشعار")
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, verbose_name="نطاق الإرسال")
    
    # إحصائيات
    target_count = models.IntegerField(default=0, verbose_name="عدد المستهدفين")
    sent_count = models.IntegerField(default=0, verbose_name="عدد المرسل")
    success_count = models.IntegerField(default=0, verbose_name="عدد الناجح")
    failed_count = models.IntegerField(default=0, verbose_name="عدد الفاشل")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    
    class Meta:
        verbose_name = "سجل إشعار تاجر"
        verbose_name_plural = "سجل إشعارات التجار"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.merchant.business_name} - {self.title} ({self.created_at.strftime('%Y-%m-%d')})"
