"""
سكريبت لإضافة ميزة إعدادات المتواجدين إلى Django Admin
"""

import os
import sys

def add_to_models():
    """إضافة النموذج إلى models.py"""
    print("1. إضافة النموذج إلى api/models.py...")
    
    model_code = """

# ============= Online Users Settings Model =============
from django.core.validators import MinValueValidator, MaxValueValidator

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
            OnlineUsersSettings.objects.all().delete()
        super().save(*args, **kwargs)
"""
    
    with open('api/models.py', 'a', encoding='utf-8') as f:
        f.write(model_code)
    print("✅ تم إضافة النموذج")

def add_to_admin():
    """إضافة Admin"""
    print("2. إضافة Admin إلى api/admin.py...")
    
    admin_code = """

# ============= Online Users Settings Admin =============
from api.models import OnlineUsersSettings

@admin.register(OnlineUsersSettings)
class OnlineUsersSettingsAdmin(admin.ModelAdmin):
    '''لوحة تحكم إعدادات المتواجدين'''
    
    fieldsets = (
        ('الإعدادات الأساسية', {
            'fields': ('enabled', 'display_mode', 'position', ('color_scheme', 'custom_color'), 'opacity'),
        }),
        ('إعدادات العرض', {
            'fields': ('show_activity_status', 'show_mini_chart', 'show_pulse_animation', 'auto_hide_on_scroll', 'show_only_on_homepage'),
            'classes': ('collapse',),
        }),
        ('الإعدادات المتقدمة', {
            'fields': ('update_interval', ('min_users', 'max_users'), ('peak_hours_start', 'peak_hours_end')),
            'classes': ('collapse',),
        }),
        ('المؤثرات', {
            'fields': ('sound_effects', 'vibration_feedback'),
            'classes': ('collapse',),
        }),
    )
    
    list_display = ('get_status', 'enabled', 'display_mode', 'position', 'min_users', 'max_users', 'updated_at')
    list_editable = ('enabled', 'display_mode', 'position', 'min_users', 'max_users')
    
    def get_status(self, obj):
        return '🟢 مفعل' if obj.enabled else '🔴 معطل'
    get_status.short_description = 'الحالة'
    
    def has_add_permission(self, request):
        return not OnlineUsersSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
"""
    
    with open('api/admin.py', 'a', encoding='utf-8') as f:
        f.write(admin_code)
    print("✅ تم إضافة Admin")

def add_to_serializers():
    """إضافة Serializer"""
    print("3. إضافة Serializer إلى api/serializers.py...")
    
    serializer_code = """

# ============= Online Users Settings Serializer =============
class OnlineUsersSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineUsersSettings
        fields = '__all__'
"""
    
    with open('api/serializers.py', 'a', encoding='utf-8') as f:
        f.write(serializer_code)
    print("✅ تم إضافة Serializer")

def add_to_views():
    """إضافة Views"""
    print("4. إضافة View إلى api/views.py...")
    
    view_code = """

# ============= Online Users Settings View =============
class OnlineUsersSettingsView(APIView):
    '''API لجلب إعدادات المتواجدين'''
    permission_classes = [AllowAny]
    
    def get(self, request):
        settings, created = OnlineUsersSettings.objects.get_or_create(pk=1)
        serializer = OnlineUsersSettingsSerializer(settings)
        return Response(serializer.data)
"""
    
    with open('api/views.py', 'a', encoding='utf-8') as f:
        f.write(view_code)
    print("✅ تم إضافة View")

def add_to_urls():
    """إضافة URL"""
    print("5. إضافة URL...")
    
    # قراءة ملف URLs
    with open('api/urls.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إضافة import إذا لم يكن موجوداً
    if 'OnlineUsersSettingsView' not in content:
        import_line = "from .views import OnlineUsersSettingsView\n"
        content = content.replace('from .views import', f'{import_line}from .views import')
    
    # إضافة URL
    url_line = "    path('online-users-settings/', OnlineUsersSettingsView.as_view(), name='online-users-settings'),\n"
    if 'online-users-settings' not in content:
        # إضافة قبل آخر قوس
        content = content.replace(']', f'{url_line}]')
    
    with open('api/urls.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم إضافة URL")

def main():
    print("=" * 50)
    print("إضافة ميزة إعدادات المتواجدين إلى Django Admin")
    print("=" * 50)
    
    try:
        add_to_models()
        add_to_admin()
        add_to_serializers()
        add_to_views()
        add_to_urls()
        
        print("\n" + "=" * 50)
        print("✅ تمت إضافة جميع الملفات بنجاح!")
        print("=" * 50)
        
        print("\nالخطوات التالية:")
        print("1. تشغيل: python manage.py makemigrations")
        print("2. تشغيل: python manage.py migrate")
        print("3. فتح Django Admin والبحث عن 'إعدادات المتواجدين'")
        
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
