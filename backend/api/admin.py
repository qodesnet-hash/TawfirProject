from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Governorate, City, Category, Merchant, Offer, OfferImage, Favorite, Review, MerchantRequest, BusinessType, ExchangeRate


# ============= Exchange Rate Admin =============
@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    """إدارة أسعار الصرف"""
    list_display = ['get_currency_icon', 'currency_code', 'get_region_badge', 'get_rate_display', 'is_active', 'updated_at']
    list_editable = ['is_active']
    list_filter = ['region', 'currency_code', 'is_active']
    search_fields = ['currency_code']
    ordering = ['region', 'currency_code']
    
    fieldsets = (
        ('معلومات سعر الصرف', {
            'fields': ('currency_code', 'region', 'rate')
        }),
        ('الإعدادات', {
            'fields': ('is_active',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_currency_icon(self, obj):
        icons = {
            'SAR': '🇸🇦',
            'USD': '🇺🇸',
        }
        icon = icons.get(obj.currency_code, '💰')
        return format_html('<span style="font-size: 24px;">{}</span>', icon)
    get_currency_icon.short_description = ''
    
    def get_region_badge(self, obj):
        colors = {'north': '#3b82f6', 'south': '#10b981'}
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{}</span>',
            colors.get(obj.region, '#6b7280'), obj.get_region_display()
        )
    get_region_badge.short_description = 'المنطقة'
    
    def get_rate_display(self, obj):
        return format_html(
            '<span style="font-size: 16px; font-weight: bold; color: #059669;">1 {} = {:,.0f} ر.ي</span>',
            obj.get_currency_code_display(), obj.rate
        )
    get_rate_display.short_description = 'سعر الصرف'


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
        'get_region_badge',
        'get_cities_count',
        'get_offers_count',
        'get_color_display',
        'order',
        'is_active',
        'updated_at'
    )
    
    list_editable = ('order', 'is_active')
    list_filter = ('region', 'is_active', 'created_at')
    search_fields = ('name', 'name_en', 'description')
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': (
                'name',
                'name_en',
                'region',
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
    
    def get_region_badge(self, obj):
        """عرض المنطقة"""
        colors = {'north': '#3b82f6', 'south': '#10b981'}
        icons = {'north': '⬆️', 'south': '⬇️'}
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{} {}</span>',
            colors.get(obj.region, '#6b7280'), icons.get(obj.region, ''), obj.get_region_display()
        )
    get_region_badge.short_description = 'المنطقة'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """إدارة الفئات"""
    list_display = ['get_icon_display', 'get_name_link', 'name_en', 'get_offers_count', 'get_color_display', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'name_en']
    
    class Media:
        js = (
            'https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.js',
        )
    
    def get_icon_display(self, obj):
        if obj.icon:
            return format_html(
                '<span style="display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; background: {}15; border-radius: 8px;">' 
                '<ion-icon name="{}" style="font-size: 24px; color: {};"></ion-icon>'
                '</span>',
                obj.color or '#666',
                obj.icon,
                obj.color or '#666'
            )
        return format_html(
            '<span style="color: #999; font-size: 12px;">—</span>'
        )
    get_icon_display.short_description = 'الأيقونة'
    
    def get_name_link(self, obj):
        """عرض الاسم مع رابط للتعديل"""
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('admin:api_category_change', args=[obj.pk])
        return format_html(
            '<a href="{}" style="font-weight: 600; color: #2563eb; text-decoration: none;">{}</a>',
            url,
            obj.name
        )
    get_name_link.short_description = 'الفئة'
    get_name_link.admin_order_field = 'name'
    
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

# ============= Business Type Admin =============
@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    """إدارة أنواع الأنشطة التجارية"""
    list_display = ['name', 'icon', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['order', 'name']

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

# ============= Payment Accounts Admin =============
from .models import PaymentAccount, FeaturedPlan, FeaturedRequest

@admin.register(PaymentAccount)
class PaymentAccountAdmin(admin.ModelAdmin):
    """إدارة حسابات الدفع"""
    list_display = ['get_bank_icon', 'bank_name', 'account_name', 'account_number', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['bank_name', 'is_active']
    search_fields = ['account_name', 'account_number']
    
    fieldsets = (
        ('معلومات الحساب', {
            'fields': ('bank_name', 'account_name', 'account_number')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'get_qr_preview'),
            'description': 'ارفع QR Code لرقم الحساب (مختار)'
        }),
        ('إعدادات', {
            'fields': ('is_active', 'order', 'notes')
        }),
    )
    
    readonly_fields = ['get_qr_preview', 'created_at', 'updated_at']
    
    def get_bank_icon(self, obj):
        icons = {
            'alkremi': '💳',
            'alomgy': '🏛️',
            'cac': '🏦',
            'tadhamon': '💵',
            'other': '💰'
        }
        icon = icons.get(obj.bank_name, '💰')
        return format_html(
            '<span style="font-size: 24px;">{}</span>',
            icon
        )
    get_bank_icon.short_description = ''
    
    def get_qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" style="max-width: 200px; border: 2px solid #ddd; border-radius: 8px; padding: 10px;" />',
                obj.qr_code.url
            )
        return 'لم يتم رفع QR Code'
    get_qr_preview.short_description = 'معاينة QR Code'

# ============= Featured Plans Admin =============
@admin.register(FeaturedPlan)
class FeaturedPlanAdmin(admin.ModelAdmin):
    """إدارة الخطط الإعلانية"""
    list_display = ['get_plan_icon', 'name', 'duration_days', 'get_price_display', 'estimated_views', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'duration_days']
    search_fields = ['name']
    
    fieldsets = (
        ('معلومات الخطة', {
            'fields': ('name', 'duration_days', 'price', 'discount_percentage')
        }),
        ('التفاصيل', {
            'fields': ('estimated_views', 'features'),
            'description': 'كل ميزة في سطر منفصل'
        }),
        ('إعدادات', {
            'fields': ('is_active', 'order')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_plan_icon(self, obj):
        if obj.duration_days <= 7:
            return '📅'  # Calendar
        elif obj.duration_days <= 14:
            return '📆'  # Calendar with dates
        elif obj.duration_days <= 30:
            return '🗓️'  # Calendar pad
        else:
            return '📅'  # Default
    get_plan_icon.short_description = ''
    
    def get_price_display(self, obj):
        try:
            if obj.discount_percentage > 0:
                discounted = float(obj.discounted_price)
                original = float(obj.price)
                # Format numbers first, then pass to format_html
                original_formatted = f"{original:,.0f}"
                discounted_formatted = f"{discounted:,.0f}"
                return format_html(
                    '<div>'
                    '<span style="text-decoration: line-through; color: #999; font-size: 12px;">{} ر.ي</span><br>'
                    '<span style="color: #10b981; font-weight: bold;">{} ر.ي</span> '
                    '<span style="background: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">-{}%</span>'
                    '</div>',
                    original_formatted,
                    discounted_formatted,
                    obj.discount_percentage
                )
            price_formatted = f"{float(obj.price):,.0f}"
            return format_html(
                '<span style="font-weight: bold;">{} ر.ي</span>',
                price_formatted
            )
        except Exception as e:
            return str(obj.price)
    get_price_display.short_description = 'السعر'

# ============= Featured Requests Admin =============
@admin.register(FeaturedRequest)
class FeaturedRequestAdmin(admin.ModelAdmin):
    """إدارة طلبات الإعلانات المميزة"""
    list_display = [
        'get_status_badge',
        'get_merchant_name',
        'get_offer_title',
        'plan',
        'get_receipt_status',
        'get_dates_info',
        'get_stats',
        'created_at'
    ]
    
    list_filter = ['status', 'plan', 'created_at', 'payment_method']
    search_fields = [
        'merchant__business_name',
        'offer__title',
        'transaction_number'
    ]
    
    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('merchant', 'offer', 'plan', 'status')
        }),
        ('معلومات الدفع', {
            'fields': (
                'payment_method',
                'transaction_number',
                'payment_receipt',
                'get_receipt_preview'
            )
        }),
        ('التواريخ', {
            'fields': ('start_date', 'end_date', 'get_remaining_time')
        }),
        ('الإحصائيات', {
            'fields': ('views_count', 'favorites_count', 'clicks_count'),
            'classes': ('collapse',)
        }),
        ('ملاحظات الإدارة', {
            'fields': ('admin_notes', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at', 'reviewed_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'reviewed_at',
        'get_receipt_preview',
        'get_remaining_time'
    ]
    
    actions = ['activate_requests', 'reject_requests']
    
    def get_status_badge(self, obj):
        colors = {
            'draft': '#6b7280',
            'pending': '#f59e0b',
            'active': '#10b981',
            'rejected': '#ef4444',
            'expired': '#9ca3af'
        }
        icons = {
            'draft': '📋',
            'pending': '⏳',
            'active': '✅',
            'rejected': '❌',
            'expired': '⏰'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; display: inline-flex; align-items: center; gap: 4px; font-size: 12px;">{} {}</span>',
            colors.get(obj.status, '#6b7280'),
            icons.get(obj.status, ''),
            obj.get_status_display()
        )
    get_status_badge.short_description = 'الحالة'
    
    def get_merchant_name(self, obj):
        from django.urls import reverse
        url = reverse('admin:api_merchant_change', args=[obj.merchant.pk])
        return format_html(
            '<a href="{}" style="color: #2563eb; font-weight: 500;">{}</a>',
            url,
            obj.merchant.business_name
        )
    get_merchant_name.short_description = 'التاجر'
    
    def get_offer_title(self, obj):
        from django.urls import reverse
        url = reverse('admin:api_offer_change', args=[obj.offer.pk])
        title = obj.offer.title[:40] + '...' if len(obj.offer.title) > 40 else obj.offer.title
        return format_html(
            '<a href="{}" style="color: #10b981;">{}</a>',
            url,
            title
        )
    get_offer_title.short_description = 'العرض'
    
    def get_receipt_status(self, obj):
        if obj.payment_receipt:
            return format_html(
                '<span style="color: #10b981;">✅ تم الرفع</span>'
            )
        return format_html(
            '<span style="color: #ef4444;">❌ لم يتم الرفع</span>'
        )
    get_receipt_status.short_description = 'الإيصال'
    
    def get_dates_info(self, obj):
        if obj.start_date and obj.end_date:
            if obj.is_active:
                return format_html(
                    '<div style="font-size: 11px;">📅 {}<br>🎯 باقي {} يوم</div>',
                    obj.start_date.strftime('%Y-%m-%d'),
                    obj.days_remaining
                )
            return format_html(
                '<div style="font-size: 11px; color: #999;">{} - {}</div>',
                obj.start_date.strftime('%Y-%m-%d'),
                obj.end_date.strftime('%Y-%m-%d')
            )
        return '-'
    get_dates_info.short_description = 'الفترة'
    
    def get_stats(self, obj):
        return format_html(
            '<div style="font-size: 11px; display: flex; gap: 8px;">👁️ {} ❤️ {} 👆 {}</div>',
            obj.views_count,
            obj.favorites_count,
            obj.clicks_count
        )
    get_stats.short_description = 'الإحصائيات'
    
    def get_receipt_preview(self, obj):
        if obj.payment_receipt:
            if obj.payment_receipt.name.endswith('.pdf'):
                return format_html(
                    '<a href="{}" target="_blank" style="background: #3b82f6; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; display: inline-block;">📄 عرض PDF</a>',
                    obj.payment_receipt.url
                )
            else:
                return format_html(
                    '<img src="{}" style="max-width: 300px; border: 2px solid #ddd; border-radius: 8px; padding: 5px;" />',
                    obj.payment_receipt.url
                )
        return 'لم يتم رفع إيصال'
    get_receipt_preview.short_description = 'معاينة الإيصال'
    
    def get_remaining_time(self, obj):
        if obj.is_active:
            return f'باقي {obj.days_remaining} يوم'
        elif obj.status == 'expired':
            return 'انتهى'
        return '-'
    get_remaining_time.short_description = 'الوقت المتبقي'
    
    def activate_requests(self, request, queryset):
        """تفعيل الطلبات المحددة"""
        count = 0
        for req in queryset.filter(status='pending'):
            if req.activate():
                count += 1
        self.message_user(request, f'✅ تم تفعيل {count} إعلان')
    activate_requests.short_description = '✅ تفعيل الإعلانات'
    
    def reject_requests(self, request, queryset):
        """رفض الطلبات المحددة"""
        count = 0
        for req in queryset.filter(status='pending'):
            if req.reject('تم الرفض من قبل الإدارة'):
                count += 1
        self.message_user(request, f'❌ تم رفض {count} إعلان', level='WARNING')
    reject_requests.short_description = '❌ رفض الإعلانات'

# ============= Deal of the Day Admin =============
from .models import DealOfDaySettings, DealOfDayRequest

@admin.register(DealOfDaySettings)
class DealOfDaySettingsAdmin(admin.ModelAdmin):
    """إدارة إعدادات صفقة اليوم"""
    list_display = ['get_mode_badge', 'get_price_display', 'min_discount', 'max_days_per_merchant', 'is_active', 'updated_at']
    
    fieldsets = (
        ('إعدادات الوضع', {
            'fields': ('mode', 'is_active'),
            'description': 'تلقائي: يختار أعلى خصم تلقائياً | مدفوع فقط: يعرض الطلبات المدفوعة فقط'
        }),
        ('إعدادات الوضع التلقائي', {
            'fields': ('min_discount',),
            'description': 'الحد الأدنى لنسبة الخصم للعروض التلقائية'
        }),
        ('إعدادات التسعير', {
            'fields': ('price_per_day', 'max_days_per_merchant'),
        }),
    )
    
    def has_add_permission(self, request):
        # منع إضافة أكثر من سجل
        return not DealOfDaySettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_mode_badge(self, obj):
        colors = {'auto': '#10b981', 'paid': '#f59e0b'}
        icons = {'auto': '🔄', 'paid': '💰'}
        return format_html(
            '<span style="background: {}; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold;">{} {}</span>',
            colors.get(obj.mode, '#6b7280'), icons.get(obj.mode, ''), obj.get_mode_display()
        )
    get_mode_badge.short_description = 'الوضع'
    
    def get_price_display(self, obj):
        return format_html(
            '<span style="font-size: 16px; font-weight: bold; color: #059669;">{:,.0f} ر.ي/يوم</span>',
            obj.price_per_day
        )
    get_price_display.short_description = 'السعر'


@admin.register(DealOfDayRequest)
class DealOfDayRequestAdmin(admin.ModelAdmin):
    """إدارة طلبات صفقة اليوم"""
    list_display = ['get_offer_title', 'get_merchant_name', 'get_status_badge', 'duration_days', 'get_price_display', 'get_dates', 'created_at']
    list_filter = ['status', 'created_at', 'duration_days']
    search_fields = ['merchant__business_name', 'offer__title']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at', 'views_count', 'clicks_count', 'get_receipt_preview']
    ordering = ['-created_at']
    actions = ['activate_requests', 'reject_requests']
    
    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('merchant', 'offer', 'status')
        }),
        ('المدة والسعر', {
            'fields': ('duration_days', 'total_price')
        }),
        ('معلومات الدفع', {
            'fields': ('payment_method', 'transaction_number', 'payment_receipt', 'get_receipt_preview')
        }),
        ('التواريخ', {
            'fields': ('start_date', 'end_date', 'created_at', 'reviewed_at'),
            'classes': ('collapse',)
        }),
        ('الإحصائيات', {
            'fields': ('views_count', 'clicks_count'),
            'classes': ('collapse',)
        }),
        ('ملاحظات', {
            'fields': ('admin_notes', 'rejection_reason'),
            'classes': ('collapse',)
        }),
    )
    
    def get_offer_title(self, obj):
        discount = obj.offer.saving_percentage
        return format_html(
            '<div><strong>{}</strong><br><span style="color: #059669; font-size: 12px;">{}% خصم</span></div>',
            obj.offer.title[:40], discount
        )
    get_offer_title.short_description = 'العرض'
    
    def get_merchant_name(self, obj):
        return obj.merchant.business_name
    get_merchant_name.short_description = 'التاجر'
    
    def get_status_badge(self, obj):
        colors = {
            'draft': '#6b7280',
            'pending': '#f59e0b',
            'active': '#10b981',
            'rejected': '#ef4444',
            'expired': '#6b7280',
        }
        icons = {
            'draft': '✏️',
            'pending': '⏳',
            'active': '🔥',
            'rejected': '❌',
            'expired': '⏰',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px;">{} {}</span>',
            colors.get(obj.status, '#6b7280'), icons.get(obj.status, ''), obj.get_status_display()
        )
    get_status_badge.short_description = 'الحالة'
    
    def get_price_display(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #059669;">{:,.0f} ر.ي</span>',
            obj.total_price
        )
    get_price_display.short_description = 'السعر'
    
    def get_dates(self, obj):
        if obj.start_date and obj.end_date:
            return format_html(
                '<span style="font-size: 11px;">{} → {}</span>',
                obj.start_date.strftime('%Y-%m-%d'),
                obj.end_date.strftime('%Y-%m-%d')
            )
        return '-'
    get_dates.short_description = 'الفترة'
    
    def get_receipt_preview(self, obj):
        if obj.payment_receipt:
            if obj.payment_receipt.name.endswith('.pdf'):
                return format_html(
                    '<a href="{}" target="_blank" style="background: #3b82f6; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none;">📄 عرض PDF</a>',
                    obj.payment_receipt.url
                )
            else:
                return format_html(
                    '<img src="{}" style="max-width: 300px; border: 2px solid #ddd; border-radius: 8px; padding: 5px;" />',
                    obj.payment_receipt.url
                )
        return 'لم يتم رفع إيصال'
    get_receipt_preview.short_description = 'معاينة الإيصال'
    
    def activate_requests(self, request, queryset):
        """تفعيل الطلبات المحددة"""
        from datetime import timedelta
        count = 0
        for req in queryset.filter(status='pending'):
            req.status = 'active'
            req.start_date = timezone.now()
            req.end_date = req.start_date + timedelta(days=req.duration_days)
            req.reviewed_at = timezone.now()
            req.save()
            count += 1
        self.message_user(request, f'🔥 تم تفعيل {count} صفقة')
    activate_requests.short_description = '🔥 تفعيل الصفقات'
    
    def reject_requests(self, request, queryset):
        """رفض الطلبات المحددة"""
        count = queryset.filter(status='pending').update(
            status='rejected',
            rejection_reason='تم الرفض من قبل الإدارة',
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'❌ تم رفض {count} طلب', level='WARNING')
    reject_requests.short_description = '❌ رفض الطلبات'


# ============= Notifications Admin =============
from .admin_notifications import *

# ============= Push Notifications Admin =============
from .admin_push_notifications import *
