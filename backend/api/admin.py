from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Governorate, City, Category, Merchant, Offer, OfferImage, Favorite, Review, MerchantRequest

# ============= Governorate Admin =============
class CityInline(admin.TabularInline):
    """إدراج المدن داخل المحافظة"""
    model = City
    extra = 1
    fields = ('name', 'is_active', 'image')
    readonly_fields = ('image',)

@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    """إدارة المحافظات"""
    list_display = (
        'get_image_thumbnail',
        'name',
        'name_en',
        'get_cities_count',
        'get_offers_count',
        'get_color_display',
        'order',
        'is_active',
        'updated_at'
    )
    
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'name_en', 'description')
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': (
                'name',
                'name_en',
                'description',
                'population'
            )
        }),
        ('المظهر', {
            'fields': (
                'image',
                'icon',
                'color'
            )
        }),
        ('الإعدادات', {
            'fields': (
                'order',
                'is_active'
            )
        }),
        ('معلومات النظام', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CityInline]
    
    def get_image_thumbnail(self, obj):
        """عرض صورة مصغرة"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px; object-fit: cover;" />',
                obj.image.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: #f0f0f0; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: #999;">لا توجد صورة</div>'
        )
    get_image_thumbnail.short_description = 'الصورة'
    
    def get_cities_count(self, obj):
        """عرض عدد المدن"""
        count = obj.cities_count
        if count > 0:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 12px;">{}</span>',
                count
            )
        return format_html(
            '<span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 12px;">0</span>'
        )
    get_cities_count.short_description = 'عدد المدن'
    
    def get_offers_count(self, obj):
        """عرض عدد العروض"""
        count = obj.offers_count
        if count > 0:
            return format_html(
                '<span style="background: #3b82f6; color: white; padding: 2px 8px; border-radius: 12px;">{}</span>',
                count
            )
        return '-'
    get_offers_count.short_description = 'عدد العروض'
    
    def get_color_display(self, obj):
        """عرض اللون"""
        return format_html(
            '<div style="display: flex; align-items: center; gap: 5px;">'
            '<div style="width: 20px; height: 20px; background: {}; border-radius: 50%; border: 1px solid #ddd;"></div>'
            '<code>{}</code>'
            '</div>',
            obj.color,
            obj.color
        )
    get_color_display.short_description = 'اللون'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """إدارة الفئات"""
    list_display = ['get_icon_display', 'name', 'name_en', 'get_offers_count', 'get_color_display', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'name_en']
    
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/ionicons@7.1.0/dist/ionicons/ionicons.css',)
        }
        js = (
            'https://cdn.jsdelivr.net/npm/ionicons@7.1.0/dist/ionicons/ionicons.esm.js',
            'https://cdn.jsdelivr.net/npm/ionicons@7.1.0/dist/ionicons/ionicons.js',
        )
    
    def get_icon_display(self, obj):
        if obj.icon:
            return format_html(
                '<ion-icon name="{}" style="font-size: 32px; color: {}; vertical-align: middle;"></ion-icon>',
                obj.icon, obj.color or '#666'
            )
        return format_html(
            '<span style="color: #999; font-size: 12px;">—</span>'
        )
    get_icon_display.short_description = 'الأيقونة'
    
    def get_offers_count(self, obj):
        count = obj.offers_count
        if count > 0:
            return format_html(
                '<span style="background: #3b82f6; color: white; padding: 2px 8px; border-radius: 12px;">{}</span>',
                count
            )
        return '-'
    get_offers_count.short_description = 'عدد العروض'
    
    def get_color_display(self, obj):
        return format_html(
            '<div style="display: flex; align-items: center; gap: 5px;">'
            '<div style="width: 20px; height: 20px; background: {}; border-radius: 50%; border: 1px solid #ddd;"></div>'
            '<code>{}</code>'
            '</div>',
            obj.color,
            obj.color
        )
    get_color_display.short_description = 'اللون'

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'governorate', 'get_offers_count', 'is_active']
    list_filter = ['governorate', 'is_active']
    search_fields = ['name', 'governorate__name']
    list_editable = ['is_active']
    
    def get_offers_count(self, obj):
        """عدد العروض في المدينة"""
        from .models import Offer
        count = Offer.objects.filter(city=obj, status='مقبول').count()
        return count
    get_offers_count.short_description = 'عدد العروض'

@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'status']
    list_filter = ['status']
    search_fields = ['business_name', 'user__phone_number']

class OfferImageInline(admin.TabularInline):
    model = OfferImage
    extra = 1

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'merchant', 'category', 'price_before', 'price_after', 'city', 'status', 'is_featured']
    list_filter = ['status', 'is_featured', 'category', 'city']
    search_fields = ['title', 'description', 'merchant__business_name']
    inlines = [OfferImageInline]

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'offer', 'created_at']
    list_filter = ['created_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'merchant', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']

@admin.register(MerchantRequest)
class MerchantRequestAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['business_name', 'user__phone_number']
    readonly_fields = ['created_at', 'reviewed_at']
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.approve()
        self.message_user(request, f"تم قبول {queryset.count()} طلب")
    approve_requests.short_description = "قبول الطلبات المحددة"
    
    def reject_requests(self, request, queryset):
        queryset.update(status='rejected', reviewed_at=timezone.now())
        self.message_user(request, f"تم رفض {queryset.count()} طلب")
    reject_requests.short_description = "رفض الطلبات المحددة"

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

# ============= Notifications Admin =============
from .admin_notifications import *
