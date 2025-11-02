from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.image_optimizer import optimize_image, validate_image_size

# ============= Governorate Model =============
class Governorate(models.Model):
    """نموذج المحافظات"""
    name = models.CharField(max_length=100, verbose_name="اسم المحافظة")
    name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name="الاسم بالإنجليزية")
    image = models.ImageField(upload_to='governorates/', blank=True, null=True, verbose_name="صورة المحافظة")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="أيقونة", help_text="اسم الأيقونة من Ionicons")
    color = models.CharField(max_length=7, default="#3b82f6", verbose_name="اللون المميز", help_text="لون hex للمحافظة")
    description = models.TextField(blank=True, null=True, verbose_name="وصف المحافظة")
    population = models.IntegerField(blank=True, null=True, verbose_name="عدد السكان")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "محافظة"
        verbose_name_plural = "المحافظات"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def cities_count(self):
        """عدد المدن في المحافظة"""
        return self.cities.filter(is_active=True).count()
    
    @property
    def offers_count(self):
        """عدد العروض في المحافظة"""
        return Offer.objects.filter(city__governorate=self, status='مقبول').count()
    
    @property
    def active_cities(self):
        """المدن النشطة في المحافظة"""
        return self.cities.filter(is_active=True).order_by('name')

class City(models.Model):
    name = models.CharField(max_length=100)
    governorate = models.ForeignKey(
        Governorate, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='cities',
        verbose_name="المحافظة"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط؟")
    image = models.ImageField(upload_to='cities/', null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="خط العرض")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="خط الطول")

    def __str__(self):
        return self.name

# ============= Category Model =============
class Category(models.Model):
    """نموذج الفئات للعروض"""
    name = models.CharField(max_length=100, verbose_name="اسم الفئة")
    name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name="الاسم بالإنجليزية")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="أيقونة", help_text="اسم الأيقونة من Ionicons")
    color = models.CharField(max_length=7, default="#3b82f6", verbose_name="اللون")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "فئة"
        verbose_name_plural = "الفئات"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def offers_count(self):
        return self.offers.filter(status='مقبول').count()

class Merchant(models.Model):
    STATUS_CHOICES = [
        ('قيد المراجعة', 'قيد المراجعة'),
        ('مقبول', 'مقبول'),
        ('مرفوض', 'مرفوض'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255, verbose_name="الاسم التجاري")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='قيد المراجعة', verbose_name="حالة الحساب")
    
    # الموقع الجغرافي
    governorate = models.ForeignKey(
        Governorate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merchants',
        verbose_name="المحافظة"
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merchants',
        verbose_name="المدينة"
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="خط العرض")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="خط الطول")
    
    # حقول جديدة
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="رقم الهاتف")
    address = models.TextField(null=True, blank=True, verbose_name="العنوان")
    opening_hours = models.CharField(max_length=100, null=True, blank=True, verbose_name="أوقات العمل")
    logo = models.ImageField(upload_to='merchants/', null=True, blank=True, verbose_name="الشعار")
    
    @property
    def average_rating(self):
        from django.db.models import Avg
        result = self.reviews.aggregate(Avg('rating'))
        return result['rating__avg'] or 0
    
    @property
    def reviews_count(self):
        return self.reviews.count()
    
    @property
    def offers_count(self):
        return self.offer_set.filter(status='مقبول').count()
    
    @property
    def is_active_merchant(self):
        """التحقق من أن التاجر معتمد ونشط"""
        return self.status == 'مقبول'
    
    def save(self, *args, **kwargs):
        """ضغط الصورة قبل الحفظ"""
        if self.logo:
            # التحقق من حجم الصورة
            is_valid, error_msg = validate_image_size(self.logo, max_size_mb=2)
            if not is_valid:
                from django.core.exceptions import ValidationError
                raise ValidationError({'logo': error_msg})
            
            # ضغط الصورة (أقصى حجم 800x800، أقصى حجم ملف 300KB)
            self.logo = optimize_image(self.logo, max_size=(800, 800), quality=85, max_file_size_kb=300)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.business_name

class Offer(models.Model):
    STATUS_CHOICES = [
        ('مقبول', 'مقبول'),
        ('مسودة', 'مسودة'),
        ('منتهي', 'منتهي'),
    ]
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, verbose_name="التاجر")
    title = models.CharField(max_length=255, verbose_name="عنوان العرض")
    description = models.TextField(verbose_name="الوصف")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='offers', verbose_name="الفئة")
    price_before = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر قبل")
    price_after = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر بعد")
    end_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name="المدينة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='مسودة')
    is_featured = models.BooleanField(default=False, verbose_name="عرض مميز؟")
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0, verbose_name="عدد المشاهدات")

    @property
    def saving_percentage(self):
        if self.price_before > 0:
            return round(((self.price_before - self.price_after) / self.price_before) * 100)
        return 0
    
    @property
    def is_expired(self):
        if self.end_at:
            return timezone.now() > self.end_at
        return False

    def __str__(self):
        return self.title

class OfferImage(models.Model):
    offer = models.ForeignKey(Offer, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='offers/')

    def save(self, *args, **kwargs):
        """ضغط صور العروض قبل الحفظ"""
        if self.image:
            # التحقق من حجم الصورة
            is_valid, error_msg = validate_image_size(self.image, max_size_mb=3)
            if not is_valid:
                from django.core.exceptions import ValidationError
                raise ValidationError({'image': error_msg})
            
            # ضغط الصورة (أقصى حجم 1200x1200، أقصى حجم ملف 500KB)
            self.image = optimize_image(self.image, max_size=(1200, 1200), quality=85, max_file_size_kb=500)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.offer.title}"

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'offer')

    def __str__(self):
        return f'{self.user.username} likes {self.offer.title}'

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 - سيء جداً'),
        (2, '2 - سيء'),
        (3, '3 - مقبول'),
        (4, '4 - جيد'),
        (5, '5 - ممتاز'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'merchant')

    def __str__(self):
        return f'Review for {self.merchant.business_name} by {self.user.username}'

class MerchantRequest(models.Model):
    """
    نموذج لطلبات التسجيل كتاجر
    """
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'موافق عليه'),
        ('rejected', 'مرفوض'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255, verbose_name="الاسم التجاري")
    business_type = models.CharField(max_length=100, verbose_name="نوع النشاط")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    address = models.TextField(verbose_name="العنوان")
    
    # الموقع الجغرافي
    governorate = models.ForeignKey(
        Governorate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المحافظة"
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المدينة"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.business_name} - {self.status}"
    
    def approve(self):
        """الموافقة على الطلب وإنشاء حساب تاجر"""
        if self.status == 'pending':
            merchant, created = Merchant.objects.update_or_create(
                user=self.user,
                defaults={
                    'business_name': self.business_name,
                    'phone': self.phone,
                    'address': self.address,
                    'governorate': self.governorate,
                    'city': self.city,
                    'status': 'مقبول'
                }
            )
            self.status = 'approved'
            self.reviewed_at = timezone.now()
            self.save()
            
            # تحديث نوع المستخدم
            self.user.user_type = 'merchant'
            self.user.save()
            
            return merchant
        return None

# ============= Online Users Settings Model =============
class OnlineUsersSettings(models.Model):
    '''إعدادات ميزة المتواجدون الآن'''
    
    DISPLAY_MODE_CHOICES = [
        ('full', 'كامل'),
        ('compact', 'مضغوط'),
        ('minimal', 'مصغر'),
    ]
    
    POSITION_CHOICES = [
        ('bottom', 'وسط الأسفل'),
        ('bottom-left', 'يسار الأسفل'),
        ('bottom-right', 'يمين الأسفل'),
        ('floating-center', 'عائم في الوسط'), 
        ('floating-left', 'عائم يسار'),        
        ('floating-right', 'عائم يمين'),       
    ]
    
    COLOR_SCHEME_CHOICES = [
        ('dynamic', 'ديناميكي'),
        ('green', 'أخضر'),
        ('blue', 'أزرق'),
        ('purple', 'بنفسجي'),
        ('custom', 'مخصص'),
    ]
    
    enabled = models.BooleanField(default=True, verbose_name="تفعيل الميزة")
    display_mode = models.CharField(max_length=20, choices=DISPLAY_MODE_CHOICES, default='full', verbose_name="وضع العرض")
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='bottom', verbose_name="موضع العداد")
    color_scheme = models.CharField(max_length=20, choices=COLOR_SCHEME_CHOICES, default='dynamic', verbose_name="نظام الألوان")
    custom_color = models.CharField(max_length=7, blank=True, null=True, verbose_name="لون مخصص")
    opacity = models.FloatField(default=1.0, validators=[MinValueValidator(0.5), MaxValueValidator(1.0)], verbose_name="الشفافية")
    show_activity_status = models.BooleanField(default=True, verbose_name="عرض حالة النشاط")
    show_mini_chart = models.BooleanField(default=True, verbose_name="عرض الرسم البياني")
    show_pulse_animation = models.BooleanField(default=True, verbose_name="عرض النبضات")
    auto_hide_on_scroll = models.BooleanField(default=False, verbose_name="الإخفاء عند التمرير")
    show_only_on_homepage = models.BooleanField(default=False, verbose_name="الصفحة الرئيسية فقط")
    update_interval = models.IntegerField(default=10, validators=[MinValueValidator(5), MaxValueValidator(60)], verbose_name="معدل التحديث (ثانية)")
    min_users = models.IntegerField(default=25, validators=[MinValueValidator(1)], verbose_name="الحد الأدنى")
    max_users = models.IntegerField(default=450, validators=[MinValueValidator(10)], verbose_name="الحد الأقصى")
    peak_hours_start = models.IntegerField(default=18, validators=[MinValueValidator(0), MaxValueValidator(23)], verbose_name="بداية الذروة")
    peak_hours_end = models.IntegerField(default=23, validators=[MinValueValidator(0), MaxValueValidator(23)], verbose_name="نهاية الذروة")
    sound_effects = models.BooleanField(default=False, verbose_name="المؤثرات الصوتية")
    vibration_feedback = models.BooleanField(default=False, verbose_name="الاهتزاز")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "إعدادات المتواجدين"
        verbose_name_plural = "إعدادات المتواجدين"
    
    def __str__(self):
        return f"إعدادات المتواجدين - {'مفعل' if self.enabled else 'معطل'}"
    
    def save(self, *args, **kwargs):
        # يضمن وجود صف واحد فقط من الإعدادات
        if not self.pk and OnlineUsersSettings.objects.exists():
            # لا تقم بحذف، بل قم بتحديث الموجود أو منع الإنشاء
            # الطريقة الأبسط هي منع إنشاء سجل جديد
            from django.core.exceptions import ValidationError
            raise ValidationError("يمكن إنشاء سجل إعدادات واحد فقط.")
        super().save(*args, **kwargs)

# ============= Notifications Models =============
from .models_notifications import FCMToken, Notification