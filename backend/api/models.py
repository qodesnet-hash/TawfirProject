from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.image_optimizer import optimize_image, validate_image_size

# ============= Exchange Rate Model =============
class ExchangeRate(models.Model):
    """نموذج أسعار الصرف حسب المنطقة"""
    REGION_CHOICES = [
        ('north', 'شمال'),
        ('south', 'جنوب'),
    ]
    
    CURRENCY_CHOICES = [
        ('SAR', 'ريال سعودي'),
        ('USD', 'دولار أمريكي'),
    ]
    
    currency_code = models.CharField(max_length=10, choices=CURRENCY_CHOICES, verbose_name="العملة")
    region = models.CharField(max_length=10, choices=REGION_CHOICES, verbose_name="المنطقة")
    rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر بالريال اليمني")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "سعر صرف"
        verbose_name_plural = "أسعار الصرف"
        unique_together = ['currency_code', 'region']
        ordering = ['region', 'currency_code']
    
    def __str__(self):
        return f"{self.get_currency_code_display()} - {self.get_region_display()}: {self.rate} ر.ي"


# ============= Governorate Model =============
class Governorate(models.Model):
    """نموذج المحافظات"""
    REGION_CHOICES = [
        ('north', 'شمال'),
        ('south', 'جنوب'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="اسم المحافظة")
    name_en = models.CharField(max_length=100, blank=True, null=True, verbose_name="الاسم بالإنجليزية")
    region = models.CharField(max_length=10, choices=REGION_CHOICES, default='north', verbose_name="المنطقة")
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

# ============= Business Type Model =============
class BusinessType(models.Model):
    """نموذج أنواع الأنشطة التجارية"""
    name = models.CharField(max_length=100, verbose_name="اسم النشاط")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="أيقونة", help_text="اسم الأيقونة من Ionicons")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "نوع نشاط"
        verbose_name_plural = "أنواع الأنشطة"
        ordering = ['order', 'name']
    
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
    business_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="نوع النشاط")
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
    
    # خدمة التوصيل
    delivery_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="رقم التوصيل (واتساب)")
    
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
    
    CURRENCY_CHOICES = [
        ('YER', 'ر.ي'),
        ('SAR', 'ر.س'),
        ('USD', '$'),
    ]
    
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, verbose_name="التاجر")
    title = models.CharField(max_length=255, verbose_name="عنوان العرض")
    description = models.TextField(verbose_name="الوصف")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='offers', verbose_name="الفئة")
    price_before = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر قبل")
    price_after = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر بعد")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='YER', verbose_name="العملة")
    end_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name="المدينة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='مسودة')
    is_featured = models.BooleanField(default=False, verbose_name="عرض مميز؟")
    featured_until = models.DateTimeField(null=True, blank=True, verbose_name="مميز حتى")
    is_deal_of_day = models.BooleanField(default=False, verbose_name="صفقة اليوم؟")
    deal_of_day_until = models.DateTimeField(null=True, blank=True, verbose_name="صفقة اليوم حتى")
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0, verbose_name="عدد المشاهدات")
    delivery_enabled = models.BooleanField(default=False, verbose_name="تفعيل التوصيل")
    
    @property
    def currency_symbol(self):
        """إرجاع رمز العملة"""
        symbols = {
            'YER': 'ر.ي',
            'SAR': 'ر.س',
            'USD': '$',
        }
        return symbols.get(self.currency, 'ر.ي')

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
    merchant = models.ForeignKey(Merchant, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="حساب التاجر")
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
            self.merchant = merchant
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
        if not self.pk and OnlineUsersSettings.objects.exists():
            from django.core.exceptions import ValidationError
            raise ValidationError("يمكن إنشاء سجل إعدادات واحد فقط.")
        super().save(*args, **kwargs)

# ============= Payment Accounts Model =============
class PaymentAccount(models.Model):
    """حسابات الدفع"""
    BANK_CHOICES = [
        ('alkremi', 'الكريمي'),
        ('alomgy', 'العمقي'),
        ('cac', 'بنك التسليف'),
        ('tadhamon', 'بنك التضامن'),
        ('other', 'أخرى'),
    ]
    
    bank_name = models.CharField(max_length=50, choices=BANK_CHOICES, verbose_name="البنك")
    account_name = models.CharField(max_length=255, verbose_name="اسم الحساب")
    account_number = models.CharField(max_length=50, verbose_name="رقم الحساب")
    qr_code = models.ImageField(upload_to='payment_qr/', null=True, blank=True, verbose_name="QR Code")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "حساب دفع"
        verbose_name_plural = "حسابات الدفع"
        ordering = ['order', 'bank_name']
    
    def __str__(self):
        return f"{self.get_bank_name_display()} - {self.account_number}"

# ============= Featured Plans Model =============
class FeaturedPlan(models.Model):
    """خطط الإعلانات المميزة"""
    name = models.CharField(max_length=100, verbose_name="اسم الخطة")
    duration_days = models.IntegerField(verbose_name="المدة بالأيام")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر (ريال يمني)")
    estimated_views = models.CharField(max_length=50, blank=True, null=True, verbose_name="المشاهدات المتوقعة")
    features = models.TextField(blank=True, null=True, verbose_name="الميزات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    discount_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="نسبة الخصم %")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "خطة إعلانية"
        verbose_name_plural = "الخطط الإعلانية"
        ordering = ['order', 'duration_days']
    
    def __str__(self):
        return f"{self.name} - {self.duration_days} أيام"
    
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

# ============= Featured Request Model =============
class FeaturedRequest(models.Model):
    """طلبات الإعلانات المميزة"""
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('pending', 'قيد المراجعة'),
        ('active', 'نشط'),
        ('rejected', 'مرفوض'),
        ('expired', 'منتهي'),
    ]
    
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='featured_requests', verbose_name="التاجر")
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='featured_requests', verbose_name="العرض")
    plan = models.ForeignKey(FeaturedPlan, on_delete=models.PROTECT, verbose_name="الخطة")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")
    
    payment_receipt = models.FileField(upload_to='featured_receipts/', null=True, blank=True, verbose_name="إيصال الدفع")
    payment_method = models.ForeignKey(PaymentAccount, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="طريقة الدفع")
    transaction_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم الحوالة")
    
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ البدء")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    
    views_count = models.IntegerField(default=0, verbose_name="عدد المشاهدات")
    favorites_count = models.IntegerField(default=0, verbose_name="الإضافة للمفضلة")
    clicks_count = models.IntegerField(default=0, verbose_name="عدد الضغطات")
    
    admin_notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات الإدارة")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="سبب الرفض")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المراجعة")
    
    class Meta:
        verbose_name = "طلب إعلان مميز"
        verbose_name_plural = "طلبات الإعلانات المميزة"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.merchant.business_name} - {self.offer.title} ({self.get_status_display()})"
    
    @property
    def is_active(self):
        if self.status == 'active' and self.end_date:
            return timezone.now() <= self.end_date
        return False
    
    @property
    def days_remaining(self):
        if self.is_active and self.end_date:
            remaining = self.end_date - timezone.now()
            return max(0, remaining.days)
        return 0
    
    @property
    def total_price(self):
        return self.plan.discounted_price
    
    def activate(self):
        if self.status == 'pending':
            from datetime import timedelta
            self.status = 'active'
            self.start_date = timezone.now()
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
            self.reviewed_at = timezone.now()
            self.offer.is_featured = True
            self.offer.save()
            self.save()
            return True
        return False
    
    def reject(self, reason=None):
        if self.status == 'pending':
            self.status = 'rejected'
            self.rejection_reason = reason
            self.reviewed_at = timezone.now()
            self.save()
            return True
        return False
    
    def check_expiration(self):
        if self.status == 'active' and self.end_date and timezone.now() > self.end_date:
            self.status = 'expired'
            self.offer.is_featured = False
            self.offer.featured_until = None
            self.offer.save()
            self.save()
            return True
        return False
    
    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = FeaturedRequest.objects.filter(pk=self.pk).first()
            if old_instance:
                if old_instance.status != 'active' and self.status == 'active':
                    from datetime import timedelta
                    if not self.start_date:
                        self.start_date = timezone.now()
                    if not self.end_date:
                        self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
                    if not self.reviewed_at:
                        self.reviewed_at = timezone.now()
                    self.offer.is_featured = True
                    self.offer.featured_until = self.end_date
                    self.offer.save()
                    print(f"✅ Auto-Activated Featured Ad: {self.offer.title} until {self.end_date}")
                elif old_instance.status == 'active' and self.status in ['rejected', 'expired']:
                    self.offer.is_featured = False
                    self.offer.featured_until = None
                    self.offer.save()
                    print(f"❌ Auto-Deactivated Featured Ad: {self.offer.title}")
        super().save(*args, **kwargs)

# ============= Deal of the Day Models =============
class DealOfDaySettings(models.Model):
    """إعدادات صفقة اليوم"""
    MODE_CHOICES = [
        ('auto', 'تلقائي'),
        ('paid', 'مدفوع فقط'),
    ]
    
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='auto', verbose_name="الوضع")
    min_discount = models.IntegerField(default=25, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="الحد الأدنى للخصم %")
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=1000, verbose_name="السعر لليوم الواحد (ر.ي)")
    max_days_per_merchant = models.IntegerField(default=7, verbose_name="الحد الأقصى للأيام لكل تاجر/أسبوع")
    is_active = models.BooleanField(default=True, verbose_name="تفعيل صفقة اليوم")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "إعدادات صفقة اليوم"
        verbose_name_plural = "إعدادات صفقة اليوم"
    
    def __str__(self):
        return f"إعدادات صفقة اليوم - {self.get_mode_display()}"
    
    def save(self, *args, **kwargs):
        # التأكد من وجود سجل واحد فقط
        if not self.pk and DealOfDaySettings.objects.exists():
            raise ValueError("يمكن إنشاء سجل إعدادات واحد فقط")
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """جلب الإعدادات أو إنشاء افتراضية"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class DealOfDayRequest(models.Model):
    """طلبات صفقة اليوم"""
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('pending', 'قيد المراجعة'),
        ('active', 'نشط'),
        ('rejected', 'مرفوض'),
        ('expired', 'منتهي'),
    ]
    
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='deal_of_day_requests', verbose_name="التاجر")
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='deal_of_day_requests', verbose_name="العرض")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")
    duration_days = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(7)], verbose_name="عدد الأيام")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر الإجمالي")
    
    payment_receipt = models.FileField(upload_to='deal_of_day_receipts/', null=True, blank=True, verbose_name="إيصال الدفع")
    payment_method = models.ForeignKey(PaymentAccount, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="طريقة الدفع")
    transaction_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم الحوالة")
    
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ البدء")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    
    views_count = models.IntegerField(default=0, verbose_name="عدد المشاهدات")
    clicks_count = models.IntegerField(default=0, verbose_name="عدد الضغطات")
    
    admin_notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات الإدارة")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="سبب الرفض")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المراجعة")
    
    class Meta:
        verbose_name = "طلب صفقة اليوم"
        verbose_name_plural = "طلبات صفقة اليوم"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.merchant.business_name} - {self.offer.title} ({self.get_status_display()})"
    
    @property
    def is_active_now(self):
        """هل الطلب نشط حالياً"""
        if self.status == 'active' and self.start_date and self.end_date:
            return self.start_date <= timezone.now() <= self.end_date
        return False
    
    @property
    def days_remaining(self):
        """الأيام المتبقية"""
        if self.is_active_now and self.end_date:
            remaining = self.end_date - timezone.now()
            return max(0, remaining.days)
        return 0
    
    def calculate_price(self):
        """حساب السعر الإجمالي"""
        settings = DealOfDaySettings.get_settings()
        return settings.price_per_day * self.duration_days
    
    def save(self, *args, **kwargs):
        # حساب السعر تلقائياً
        if not self.total_price:
            self.total_price = self.calculate_price()
        
        # عند التفعيل
        if self.pk:
            old_instance = DealOfDayRequest.objects.filter(pk=self.pk).first()
            if old_instance:
                if old_instance.status != 'active' and self.status == 'active':
                    from datetime import timedelta
                    if not self.start_date:
                        self.start_date = timezone.now()
                    if not self.end_date:
                        self.end_date = self.start_date + timedelta(days=self.duration_days)
                    if not self.reviewed_at:
                        self.reviewed_at = timezone.now()
                    # تحديث العرض
                    self.offer.is_deal_of_day = True
                    self.offer.deal_of_day_until = self.end_date
                    self.offer.save()
                    print(f"🔥 Activated Deal of Day: {self.offer.title} until {self.end_date}")
                elif old_instance.status == 'active' and self.status in ['rejected', 'expired']:
                    self.offer.is_deal_of_day = False
                    self.offer.deal_of_day_until = None
                    self.offer.save()
                    print(f"❌ Deactivated Deal of Day: {self.offer.title}")
        
        super().save(*args, **kwargs)


# ============= Notifications Models =============
from .models_notifications import FCMToken, Notification

# ============= Signals =============
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=MerchantRequest)
def auto_create_merchant_on_approval(sender, instance, created, **kwargs):
    """إنشاء حساب تاجر تلقائياً عند الموافقة على الطلب"""
    if created:
        return
    
    if instance.status == 'approved':
        if not Merchant.objects.filter(user=instance.user).exists():
            merchant = Merchant.objects.create(
                user=instance.user,
                business_name=instance.business_name,
                business_type=instance.business_type,
                phone=instance.phone,
                address=instance.address,
                governorate=instance.governorate,
                city=instance.city,
                status='مقبول'
            )
            
            instance.merchant = merchant
            instance.reviewed_at = timezone.now()
            MerchantRequest.objects.filter(pk=instance.pk).update(
                merchant=merchant,
                reviewed_at=timezone.now()
            )
            
            instance.user.user_type = 'merchant'
            instance.user.save()
            
            print(f"✅ Auto-created Merchant for: {instance.user.email} - {instance.business_name}")
