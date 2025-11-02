from django.contrib import admin
from api.models import OnlineUsersSettings

@admin.register(OnlineUsersSettings)
class OnlineUsersSettingsAdmin(admin.ModelAdmin):
    """لوحة تحكم إعدادات المتواجدين"""
    
    # تنظيم الحقول في مجموعات
    fieldsets = (
        ('الإعدادات الأساسية', {
            'fields': (
                'enabled',
                'display_mode',
                'position',
                ('color_scheme', 'custom_color'),
                'opacity',
            ),
            'classes': ('wide',),
        }),
        ('إعدادات العرض', {
            'fields': (
                'show_activity_status',
                'show_mini_chart',
                'show_pulse_animation',
                'auto_hide_on_scroll',
                'show_only_on_homepage',
            ),
            'classes': ('collapse',),
        }),
        ('الإعدادات المتقدمة', {
            'fields': (
                'update_interval',
                ('min_users', 'max_users'),
                ('peak_hours_start', 'peak_hours_end'),
            ),
            'classes': ('collapse',),
        }),
        ('المؤثرات', {
            'fields': (
                'sound_effects',
                'vibration_feedback',
            ),
            'classes': ('collapse',),
        }),
        ('معلومات النظام', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    # الحقول للقراءة فقط
    readonly_fields = ('created_at', 'updated_at')
    
    # عرض القائمة
    list_display = (
        'get_status_display',
        'enabled',
        'display_mode',
        'position',
        'color_scheme',
        'min_users',
        'max_users',
        'update_interval',
        'updated_at'
    )
    
    # فلاتر جانبية
    list_filter = (
        'enabled',
        'display_mode',
        'position',
        'color_scheme',
        'show_only_on_homepage',
    )
    
    # إمكانية التعديل المباشر من القائمة
    list_editable = (
        'enabled',
        'display_mode',
        'position',
        'min_users',
        'max_users',
    )
    
    # خيارات إضافية
    save_on_top = True
    
    def get_status_display(self, obj):
        """عرض حالة الميزة بشكل جميل"""
        if obj.enabled:
            return '🟢 مفعل'
        return '🔴 معطل'
    get_status_display.short_description = 'الحالة'
    
    def has_add_permission(self, request):
        """السماح بإضافة سجل واحد فقط"""
        if OnlineUsersSettings.objects.exists():
            return False
        return True
    
    def has_delete_permission(self, request, obj=None):
        """منع حذف الإعدادات"""
        return False
    
    def changelist_view(self, request, extra_context=None):
        """إضافة معلومات إضافية لصفحة القائمة"""
        extra_context = extra_context or {}
        
        # إضافة إحصائيات
        if OnlineUsersSettings.objects.exists():
            settings = OnlineUsersSettings.objects.first()
            extra_context['settings_info'] = {
                'نطاق المستخدمين': f'{settings.min_users} - {settings.max_users}',
                'ساعات الذروة': f'{settings.peak_hours_start}:00 - {settings.peak_hours_end}:00',
                'معدل التحديث': f'{settings.update_interval} ثانية',
            }
        
        return super().changelist_view(request, extra_context=extra_context)
