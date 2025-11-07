from rest_framework import serializers
from .models import Offer, City, Category, Merchant, OfferImage, Favorite, Review, MerchantRequest, OnlineUsersSettings 
from users.models import CustomUser
from django.db.models import Avg, Count

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'governorate', 'image']

class OfferImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferImage
        fields = ['image']

# This is the single, correct version of MerchantSerializer
class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ['id', 'business_name', 'latitude', 'longitude']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'name_en', 'icon', 'color']

class OfferSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)  # تغيير من StringRelatedField إلى CitySerializer
    category = CategorySerializer(read_only=True)  # إضافة category
    images = OfferImageSerializer(many=True, read_only=True)
    merchant = MerchantSerializer(read_only=True)
    saving_percentage = serializers.IntegerField(read_only=True)
    is_featured = serializers.BooleanField(read_only=True)  # إضافة is_featured
    end_at = serializers.DateTimeField(read_only=True)  # إضافة end_at
    views_count = serializers.IntegerField(read_only=True)  # إضافة views_count
    created_at = serializers.DateTimeField(read_only=True)  # إضافة created_at
    is_favorited = serializers.SerializerMethodField()  # إضافة is_favorited

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'description', 'price_before', 'price_after',
            'saving_percentage', 'city', 'category', 'merchant', 'images', 'is_featured', 
            'end_at', 'views_count', 'created_at', 'is_favorited'
        ]
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, 
                offer=obj
            ).exists()
        return False

class FavoriteSerializer(serializers.ModelSerializer):
    offer = OfferSerializer(read_only=True)  # Include full offer data
    
    class Meta:
        model = Favorite
        fields = ['id', 'offer']

class ReviewSerializer(serializers.ModelSerializer):
    user_phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_at', 'user_phone_number', 'user_email']
        read_only_fields = ['id', 'created_at', 'user_phone_number', 'user_email']

class ReviewCreateSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    rating = serializers.IntegerField(min_value=1, max_value=5)
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        extra_kwargs = {
            'comment': {'required': False, 'allow_blank': True, 'allow_null': True, 'default': ''}
        }
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("يجب أن يكون التقييم بين 1 و5")
        return value

# ========== SERIALIZERS للوحة تحكم التجار ==========

class MerchantRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantRequest
        fields = [
            'business_name', 'business_type',
            'phone', 'address', 'governorate', 'city'
        ]

class MerchantDashboardSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    offers_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Merchant
        fields = [
            'id', 'business_name', 'logo', 'average_rating',
            'reviews_count', 'offers_count'
        ]
    
    def validate_logo(self, value):
        """التحقق من حجم الصورة"""
        from utils.image_optimizer import validate_image_size
        
        if value:
            is_valid, error_msg = validate_image_size(value, max_size_mb=2)
            if not is_valid:
                raise serializers.ValidationError(error_msg)
        return value

class OfferManagementSerializer(serializers.ModelSerializer):
    images = OfferImageSerializer(many=True, read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'description', 'price_before', 'price_after',
            'city', 'status', 'is_featured', 'end_at', 'created_at',
            'views_count', 'images', 'favorites_count'
        ]
    
    def get_favorites_count(self, obj):
        return obj.favorite_set.count()

class TopMerchantSerializer(serializers.ModelSerializer):
    """
    Serializer لعرض أفضل المتاجر في الصفحة الرئيسية
    """
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    offers_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Merchant
        fields = [
            'id', 'business_name', 'logo', 'address',
            'average_rating', 'reviews_count', 'offers_count'
        ]

class MerchantDetailSerializer(serializers.ModelSerializer):
    """
    Serializer لعرض تفاصيل المتجر الكاملة
    """
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    offers_count = serializers.IntegerField(read_only=True)
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Merchant
        fields = [
            'id', 'business_name', 'logo', 'phone', 'address',
            'opening_hours', 'latitude', 'longitude',
            'average_rating', 'reviews_count', 'offers_count',
            'recent_reviews'
        ]
    
    def get_recent_reviews(self, obj):
        # جلب آخر 5 تقييمات
        recent = obj.reviews.order_by('-created_at')[:5]
        return ReviewSerializer(recent, many=True).data

# ============= Online Users Settings Serializer =============
class OnlineUsersSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineUsersSettings
        fields = '__all__'
