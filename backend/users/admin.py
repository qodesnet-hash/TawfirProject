from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser - Gmail Auth based"""
    model = CustomUser
    list_display = ('email', 'full_name', 'user_type', 'is_verified', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active', 'is_verified', 'merchant_verified')
    search_fields = ('email', 'full_name', 'phone_number')
    ordering = ('email',)
    
    fieldsets = (
        ('معلومات تسجيل الدخول', {
            'fields': ('email', 'password', 'google_id')
        }),
        ('المعلومات الشخصية', {
            'fields': ('full_name', 'phone_number', 'profile_picture', 'date_of_birth')
        }),
        ('الموقع', {
            'fields': ('city', 'address')
        }),
        ('نوع الحساب', {
            'fields': ('user_type', 'is_verified', 'merchant_verified', 'merchant_verified_at')
        }),
        ('الصلاحيات', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('تواريخ مهمة', {
            'fields': ('last_login', 'date_joined', 'last_activity')
        }),
        ('إضافي', {
            'fields': ('preferences', 'notification_settings', 'login_count'),
            'classes': ('collapse',)
        })
    )
    
    add_fieldsets = (
        ('إنشاء مستخدم جديد', {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'full_name', 'user_type'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'last_activity', 'login_count', 'merchant_verified_at')

# Register CustomUser only
admin.site.register(CustomUser, CustomUserAdmin)
