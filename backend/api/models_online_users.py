# api/models.py - إضافة في نهاية الملف

from django.core.validators import MinValueValidator, MaxValueValidator

class OnlineUsersSettings(models.Model):
    """إعدادات ميزة المتواجدون الآن"""
    
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
    
    # الإعدادات الأساسية
    enabled = models.BooleanField(
        default=True,
        verbose_name="تفعيل الميزة",
        help_text="إظهار أو إخفاء عداد المتواجدين"
    )
    
    display_mode = models.CharField(
        max_length=20,
        choices=DISPLAY_MODE_CHOICES,
        default='full',
        verbose_name="وضع العرض"
    )
    
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default='bottom',
        verbose_name="موضع العداد"
    )
    
    color_scheme = models.CharField(
        max_length=20,
        choices=COLOR_SCHEME_CHOICES,
        default='dynamic',
        verbose_name="نظام الألوان"
    )
    
    custom_color = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        verbose_name="لون مخصص",
        help_text="مثال: #3b82f6"
    )
    
    opacity = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(1.0)],
        verbose_name="الشفافية",
        help_text="من 0.5 إلى 1.0"
    )
    
    # إعدادات العرض
    show_activity_status = models.BooleanField(
        default=True,
        verbose_name="عرض حالة النشاط"
    )
    
    show_mini_chart = models.BooleanField(
        default=True,
        verbose_name="عرض الرسم البياني الصغير"
    )
    
    show_pulse_animation = models.BooleanField(
        default=True,
        verbose_name="عرض النبضات المتحركة"
    )
    
    auto_hide_on_scroll = models.BooleanField(
        default=False,
        verbose_name="الإخفاء عند التمرير"
    )
    
    show_only_on_homepage = models.BooleanField(
        default=False,
        verbose_name="الصفحة الرئيسية فقط"
    )
    
    # الإعدادات المتقدمة
    update_interval = models.IntegerField(
        default=10,
        validators=[MinValueValidator(5), MaxValueValidator(60)],
        verbose_name="معدل التحديث (بالثواني)"
    )
    
    min_users = models.IntegerField(
        default=25,
        validators=[MinValueValidator(1)],
        verbose_name="الحد الأدنى للمستخدمين"
    )
    
    max_users = models.IntegerField(
        default=450,
        validators=[MinValueValidator(10)],
        verbose_name="الحد الأقصى للمستخدمين"
    )
    
    peak_hours_start = models.IntegerField(
        default=18,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        verbose_name="بداية ساعات الذروة"
    )
    
    peak_hours_end = models.IntegerField(
        default=23,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        verbose_name="نهاية ساعات الذروة"
    )
    
    # المؤثرات
    sound_effects = models.BooleanField(
        default=False,
        verbose_name="المؤثرات الصوتية"
    )
    
    vibration_feedback = models.BooleanField(
        default=False,
        verbose_name="الاهتزاز"
    )
    
    # معلومات إضافية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "إعدادات المتواجدين"
        verbose_name_plural = "إعدادات المتواجدين"
    
    def __str__(self):
        return f"إعدادات المتواجدين - {'مفعل' if self.enabled else 'معطل'}"
    
    def save(self, *args, **kwargs):
        # التأكد من وجود سجل واحد فقط
        if not self.pk and OnlineUsersSettings.objects.exists():
            # حذف السجل القديم
            OnlineUsersSettings.objects.all().delete()
        super().save(*args, **kwargs)
