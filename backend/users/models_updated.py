# users/models.py - نموذج المستخدم المحدث للتسجيل بـ Gmail

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    """مدير المستخدم المخصص للتعامل مع Gmail"""
    
    def create_user(self, email, password=None, **extra_fields):
        """إنشاء مستخدم جديد بالبريد الإلكتروني"""
        if not email:
            raise ValueError('البريد الإلكتروني مطلوب')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            # For social auth, we might not have a password
            user.set_unusable_password()
            
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """إنشاء مستخدم مدير"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """نموذج المستخدم المحدث"""
    
    USER_TYPE_CHOICES = [
        ('customer', 'مستخدم عادي'),
        ('merchant', 'تاجر'),
        ('admin', 'مدير'),
    ]
    
    REGISTRATION_METHOD_CHOICES = [
        ('email', 'البريد الإلكتروني'),
        ('google', 'Google'),
        ('phone', 'رقم الهاتف'),  # للتوافق مع النظام القديم
    ]
    
    # معلومات تسجيل الدخول
    email = models.EmailField(
        unique=True,
        verbose_name='البريد الإلكتروني',
        help_text='البريد الإلكتروني الأساسي للمستخدم'
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        validators=[RegexValidator(
            regex=r'^(05|5)\d{8}$',
            message='رقم الجوال يجب أن يبدأ بـ 05 ويحتوي على 10 أرقام'
        )],
        verbose_name='رقم الجوال'
    )
    
    # معلومات شخصية
    full_name = models.CharField(
        max_length=255,
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
    
    registration_method = models.CharField(
        max_length=20,
        choices=REGISTRATION_METHOD_CHOICES,
        default='email',
        verbose_name='طريقة التسجيل'
    )
    
    google_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Google ID'
    )
    
    # معلومات إضافية
    preferences = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='التفضيلات',
        help_text='تفضيلات المستخدم مثل الفئات المفضلة والإشعارات'
    )
    
    notification_settings = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='إعدادات الإشعارات'
    )
    
    # حالة الحساب
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )
    
    is_staff = models.BooleanField(
        default=False,
        verbose_name='موظف'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='تم التحقق',
        help_text='هل تم التحقق من البريد الإلكتروني أو رقم الهاتف'
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
    
    # التواريخ
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='تاريخ الانضمام'
    )
    
    last_login = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='آخر تسجيل دخول'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخر تحديث'
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
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.full_name or self.email
    
    def get_full_name(self):
        return self.full_name
    
    def get_short_name(self):
        if self.full_name:
            return self.full_name.split()[0]
        return self.email.split('@')[0]
    
    @property
    def is_merchant(self):
        """التحقق من أن المستخدم تاجر"""
        return self.user_type == 'merchant'
    
    @property
    def is_verified_merchant(self):
        """التحقق من أن التاجر موثق"""
        return self.is_merchant and self.merchant_verified
    
    @property
    def needs_profile_completion(self):
        """التحقق من اكتمال البيانات"""
        required_fields = ['full_name', 'phone_number', 'city']
        for field in required_fields:
            if not getattr(self, field):
                return True
        return False
    
    def complete_profile(self, data):
        """إكمال بيانات الملف الشخصي"""
        for field, value in data.items():
            if hasattr(self, field):
                setattr(self, field, value)
        self.save()
    
    def verify_merchant(self):
        """توثيق التاجر"""
        if self.is_merchant:
            self.merchant_verified = True
            self.merchant_verified_at = timezone.now()
            self.save()
            return True
        return False
