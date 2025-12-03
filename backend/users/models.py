from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    """نموذج المستخدم - يدعم تسجيل الدخول بـ Gmail فقط"""
    
    USER_TYPE_CHOICES = [
        ('customer', 'مستخدم عادي'),
        ('merchant', 'تاجر'),
        ('admin', 'مدير'),
    ]
    
    # إزالة الحقول غير المطلوبة من AbstractUser
    username = None
    first_name = None
    last_name = None
    
    # حقول تسجيل الدخول الأساسية
    email = models.EmailField(
        unique=True,
        verbose_name='البريد الإلكتروني'
    )
    
    phone_number = models.CharField(
        max_length=20, 
        unique=True,
        null=True,
        blank=True,
        verbose_name='رقم الجوال'
    )
    
    # معلومات شخصية
    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='الاسم الكامل'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        verbose_name='صورة الملف الشخصي'
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاريخ الميلاد'
    )
    
    # معلومات الموقع
    city = models.ForeignKey(
        'api.City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='المدينة'
    )
    
    # المدينة المختارة حالياً (للإشعارات)
    selected_city = models.ForeignKey(
        'api.City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users_selected',
        verbose_name='المدينة المختارة'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='العنوان التفصيلي'
    )
    
    # نوع المستخدم ومعلومات التسجيل
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='customer',
        verbose_name='نوع المستخدم'
    )
    
    google_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Google ID'
    )
    
    # حالة الحساب
    is_verified = models.BooleanField(
        default=False,
        verbose_name='تم التحقق',
        help_text='هل تم التحقق من البريد الإلكتروني'
    )
    
    # للتجار فقط
    merchant_verified = models.BooleanField(
        default=False,
        verbose_name='تاجر موثق',
        help_text='هل تم التحقق من التاجر من قبل الإدارة'
    )
    
    merchant_verified_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاريخ توثيق التاجر'
    )
    
    # معلومات إضافية
    preferences = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='التفضيلات'
    )
    
    notification_settings = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='إعدادات الإشعارات'
    )
    
    # الإحصائيات
    login_count = models.IntegerField(
        default=0,
        verbose_name='عدد مرات تسجيل الدخول'
    )
    
    last_activity = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='آخر نشاط'
    )
    
    # الحقل المستخدم للمصادقة (Gmail)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'
    
    def __str__(self):
        if self.full_name:
            return self.full_name
        else:
            return self.email
    
    def get_full_name(self):
        """Return the full name of the user."""
        return self.full_name or self.email
    
    def get_short_name(self):
        """Return the short name of the user."""
        if self.full_name:
            return self.full_name.split()[0]
        else:
            return self.email.split('@')[0]
    
    @property
    def is_merchant(self):
        """Check if user is a merchant."""
        return self.user_type == 'merchant'
    
    @property
    def is_verified_merchant(self):
        """Check if merchant is verified."""
        return self.is_merchant and self.merchant_verified
    
    @property
    def needs_profile_completion(self):
        """Check if profile needs completion."""
        # التحقق من الحقول المطلوبة
        if not self.full_name:
            return True
        
        if not self.phone_number:
            return True
        
        if not self.city:
            return True
            
        return False
    
    def complete_profile(self, data):
        """Complete user profile with additional data."""
        for field, value in data.items():
            if hasattr(self, field) and value:
                setattr(self, field, value)
        self.save()
    
    def verify_merchant(self):
        """Verify merchant account."""
        if self.is_merchant:
            self.merchant_verified = True
            self.merchant_verified_at = timezone.now()
            self.save()
            return True
        return False
