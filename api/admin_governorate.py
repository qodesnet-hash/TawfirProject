from django.contrib import admin
from django.utils.html import format_html
from api.models import Governorate, City

class CityInline(admin.TabularInline):
    """Inline للمدن داخل المحافظة"""
    model = City
    extra = 1
    fields = ('name', 'is_active', 'image')
    readonly_fields = ('created_at',)

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


# Update City Admin to include governorate
class CityAdmin(admin.ModelAdmin):
    """تحديث إدارة المدن"""
    list_display = (
        'name',
        'governorate',
        'get_offers_count',
        'is_active',
        'created_at'
    )
    
    list_filter = ('governorate', 'is_active')
    search_fields = ('name', 'governorate__name')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': (
                'name',
                'governorate',
                'image',
                'coordinates'
            )
        }),
        ('الإعدادات', {
            'fields': (
                'is_active',
            )
        })
    )
    
    def get_offers_count(self, obj):
        """عدد العروض في المدينة"""
        from api.models import Offer
        count = Offer.objects.filter(city=obj, is_active=True).count()
        return count
    get_offers_count.short_description = 'عدد العروض'
