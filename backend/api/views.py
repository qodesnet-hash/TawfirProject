from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, F
from django.db import models
from .models import Offer, City, Favorite, Merchant, Review, OnlineUsersSettings, BusinessType
from .serializers import (
    OfferSerializer, CitySerializer, FavoriteSerializer,
    TopMerchantSerializer, MerchantDetailSerializer, OfferSerializer as MerchantOfferSerializer, 
    ReviewSerializer, ReviewCreateSerializer,
    OnlineUsersSettingsSerializer
)
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from math import radians, cos, sin, asin, sqrt
import random


class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = City.objects.filter(is_active=True)
        governorate = self.request.query_params.get('governorate', None)
        if governorate:
            queryset = queryset.filter(governorate_id=governorate)
        return queryset

class OfferListView(generics.ListAPIView):
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Offer.objects.filter(status='مقبول')
        city_id = self.request.query_params.get('city_id', None)
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        return queryset

class OfferDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)
        
        # زيادة عداد المشاهدات
        offer.views_count = F('views_count') + 1
        offer.save(update_fields=['views_count'])
        offer.refresh_from_db()
        
        serializer = OfferSerializer(offer, context={'request': request})
        return Response(serializer.data)

class FeaturedOfferListView(generics.ListAPIView):
    queryset = Offer.objects.filter(is_featured=True, status='مقبول')
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]

class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

class FavoriteToggleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, offer_id):
        """Toggle favorite (add or remove)"""
        offer = get_object_or_404(Offer, pk=offer_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            offer=offer
        )
        if not created:
            favorite.delete()
            return Response({
                'status': 'removed', 
                'message': 'تم إزالة العرض من المفضلة'
            })
        return Response({
            'status': 'added', 
            'message': 'تم إضافة العرض إلى المفضلة'
        })
    
    def delete(self, request, offer_id):
        """Remove from favorites"""
        try:
            favorite = Favorite.objects.get(
                user=request.user, 
                offer_id=offer_id
            )
            favorite.delete()
            return Response({
                'status': 'removed',
                'success': True,
                'message': 'تم إزالة العرض من المفضلة'
            }, status=status.HTTP_200_OK)
        except Favorite.DoesNotExist:
            return Response({
                'error': 'العرض غير موجود في المفضلة',
                'status': 'not_found'
            }, status=status.HTTP_404_NOT_FOUND)


# Views للمتاجر
class TopMerchantsView(generics.ListAPIView):
    """عرض أفضل المتاجر"""
    serializer_class = TopMerchantSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Merchant.objects.filter(status='مقبول').annotate(
            num_offers=Count('offer'),
            avg_rating=Avg('reviews__rating')
        ).filter(num_offers__gt=0).order_by('-avg_rating', '-num_offers')[:5]

class MerchantDetailView(APIView):
    """عرض تفاصيل المتجر"""
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        merchant = get_object_or_404(Merchant, pk=pk)
        
        # زيادة مشاهدات جميع عروض المتجر (اختياري)
        # merchant.offer_set.update(views_count=F('views_count') + 1)
        
        serializer = MerchantDetailSerializer(merchant, context={'request': request})
        return Response(serializer.data)

class MerchantOffersView(generics.ListAPIView):
    """عرض عروض متجر معين"""
    serializer_class = MerchantOfferSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        merchant_id = self.kwargs['merchant_id']
        return Offer.objects.filter(
            merchant_id=merchant_id,
            status='مقبول'
        ).order_by('-created_at')

class ReviewCreateView(APIView):
    """إضافة أو تحديث تقييم لمتجر"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, merchant_id):
        # تسجيل معلومات التصحيح
        print(f"="*50)
        print(f"ReviewCreateView POST - Merchant ID: {merchant_id}")
        print(f"User: {request.user} (ID: {request.user.id})")
        print(f"User email: {getattr(request.user, 'email', 'N/A')}")
        print(f"User phone: {getattr(request.user, 'phone_number', 'N/A')}")
        print(f"Request data: {request.data}")
        print(f"="*50)
        
        # التحقق من المصادقة بشكل صريح
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'يجب تسجيل الدخول أولاً', 'detail': 'Authentication credentials were not provided.'},
                status=401
            )
        
        # التحقق من وجود المتجر
        try:
            merchant = Merchant.objects.get(pk=merchant_id)
            print(f"Found merchant: {merchant.business_name}")
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'المتجر غير موجود', 'merchant_id': merchant_id},
                status=404
            )
        
        # التحقق من وجود تقييم سابق
        existing_review = Review.objects.filter(user=request.user, merchant=merchant).first()
        
        if existing_review:
            # تحديث التقييم الموجود
            print(f"🔄 UPDATING existing review ID={existing_review.id}")
            print(f"   Old: rating={existing_review.rating}, comment='{existing_review.comment}'")
            print(f"   New: {request.data}")
            
            # تحديث مباشر بدون serializer لضمان الحفظ
            old_rating = existing_review.rating
            old_comment = existing_review.comment
            
            new_rating = request.data.get('rating', existing_review.rating)
            new_comment = request.data.get('comment', existing_review.comment)
            
            existing_review.rating = new_rating
            existing_review.comment = new_comment
            existing_review.save()
            
            # التحقق من الحفظ
            existing_review.refresh_from_db()
            print(f"   ✅ After save: rating={existing_review.rating}, comment='{existing_review.comment}'")
            
            if existing_review.rating != new_rating or existing_review.comment != new_comment:
                print(f"   ❌ WARNING: Values didn't save correctly!")
            
            response_serializer = ReviewSerializer(existing_review)
            return Response(
                {
                    'message': 'تم تحديث التقييم بنجاح',
                    'action': 'updated',
                    'review': response_serializer.data,
                    'debug': {
                        'old_rating': old_rating,
                        'new_rating': existing_review.rating,
                        'old_comment': old_comment,
                        'new_comment': existing_review.comment
                    }
                }, 
                status=200
            )
        else:
            # إنشاء تقييم جديد
            print(f"➕ CREATING new review for user {request.user.id} on merchant {merchant_id}")
            
            new_rating = request.data.get('rating')
            new_comment = request.data.get('comment', '')
            
            if not new_rating or not (1 <= int(new_rating) <= 5):
                return Response(
                    {'error': 'التقييم يجب أن يكون بين 1 و 5'},
                    status=400
                )
            
            try:
                review = Review.objects.create(
                    user=request.user,
                    merchant=merchant,
                    rating=int(new_rating),
                    comment=new_comment or ''
                )
                print(f"   ✅ Review created: ID={review.id}, rating={review.rating}")
                
                response_serializer = ReviewSerializer(review)
                return Response(
                    {
                        'message': 'تم إضافة التقييم بنجاح',
                        'action': 'created',
                        'review': response_serializer.data
                    },
                    status=201
                )
            except Exception as e:
                print(f"   ❌ Error creating review: {str(e)}")
                import traceback
                traceback.print_exc()
                return Response(
                    {'error': f'حدث خطأ في حفظ المراجعة: {str(e)}'},
                    status=500
                )

class ReviewUpdateView(APIView):
    """تحديث تقييم موجود"""
    permission_classes = [IsAuthenticated]
    
    def put(self, request, merchant_id):
        print(f"="*50)
        print(f"ReviewUpdateView PUT - Merchant ID: {merchant_id}")
        print(f"User: {request.user} (ID: {request.user.id})")
        print(f"Request data: {request.data}")
        print(f"="*50)
        
        # التحقق من وجود المتجر
        try:
            merchant = Merchant.objects.get(pk=merchant_id)
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'المتجر غير موجود'},
                status=404
            )
        
        # البحث عن المراجعة الموجودة
        try:
            review = Review.objects.get(user=request.user, merchant=merchant)
            print(f"Found existing review: ID={review.id}, Rating={review.rating}, Comment={review.comment}")
        except Review.DoesNotExist:
            return Response(
                {'error': 'لم تقم بتقييم هذا المتجر بعد'},
                status=404
            )
        
        # تحديث مباشر
        old_rating = review.rating
        old_comment = review.comment
        
        new_rating = request.data.get('rating', review.rating)
        new_comment = request.data.get('comment', review.comment)
        
        review.rating = new_rating
        review.comment = new_comment
        review.save()
        
        review.refresh_from_db()
        print(f"✅ Review updated: ID={review.id}, New Rating={review.rating}, New Comment={review.comment}")
        
        response_serializer = ReviewSerializer(review)
        return Response(
            {
                'message': 'تم تحديث التقييم بنجاح',
                'action': 'updated',
                'review': response_serializer.data,
                'debug': {
                    'old_rating': old_rating,
                    'new_rating': review.rating,
                    'old_comment': old_comment,
                    'new_comment': review.comment
                }
            },
            status=200
        )
    
    def delete(self, request, merchant_id):
        """حذف تقييم"""
        print(f"ReviewUpdateView DELETE - User: {request.user}")
        print(f"ReviewUpdateView DELETE - Merchant ID: {merchant_id}")
        
        try:
            merchant = Merchant.objects.get(pk=merchant_id)
            review = Review.objects.get(user=request.user, merchant=merchant)
            review_id = review.id
            review.delete()
            print(f"✅ Review {review_id} deleted successfully")
            return Response(
                {'message': 'تم حذف التقييم بنجاح'},
                status=200
            )
        except Merchant.DoesNotExist:
            print(f"❌ Merchant {merchant_id} not found")
            return Response(
                {'error': 'المتجر غير موجود'},
                status=404
            )
        except Review.DoesNotExist:
            print(f"❌ Review not found for user {request.user} and merchant {merchant_id}")
            return Response(
                {'error': 'التقييم غير موجود'},
                status=404
            )

class MerchantReviewListView(generics.ListAPIView):
    """عرض تقييمات متجر معين"""
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        merchant_id = self.kwargs['merchant_id']
        return Review.objects.filter(merchant_id=merchant_id).order_by('-created_at')

class LatestReviewsView(generics.ListAPIView):
    """عرض آخر التقييمات"""
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    queryset = Review.objects.all().order_by('-created_at')[:10]


class NearbyOffersView(APIView):
    """عرض العروض القريبة من المستخدم"""
    permission_classes = [AllowAny]
    
    def haversine(self, lon1, lat1, lon2, lat2):
        """حساب المسافة بين نقطتين GPS"""
        # تحويل من درجات إلى راديان
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        # معادلة haversine
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # نصف قطر الأرض بالكيلومتر
        return c * r
    
    def get(self, request):
        # جلب المعاملات
        user_lat = request.query_params.get('latitude')
        user_lon = request.query_params.get('longitude')
        user_city_id = request.query_params.get('city_id')
        use_gps = request.query_params.get('use_gps', 'false').lower() == 'true'
        
        # البدء بجميع العروض المقبولة
        offers = Offer.objects.filter(status='مقبول')
        
        if use_gps and user_lat and user_lon:
            try:
                user_lat = float(user_lat)
                user_lon = float(user_lon)
                
                # جلب جميع العروض مع بيانات المتاجر
                offers_with_distance = []
                
                for offer in offers.select_related('merchant', 'city'):
                    # إذا كان للمتجر إحداثيات
                    if offer.merchant and offer.merchant.latitude and offer.merchant.longitude:
                        distance = self.haversine(
                            user_lon, user_lat,
                            float(offer.merchant.longitude), 
                            float(offer.merchant.latitude)
                        )
                        offers_with_distance.append({
                            'offer': offer,
                            'distance': distance
                        })
                    # إذا كانت المدينة لها إحداثيات افتراضية
                    elif offer.city and hasattr(offer.city, 'latitude') and offer.city.latitude:
                        distance = self.haversine(
                            user_lon, user_lat,
                            float(offer.city.longitude or 0), 
                            float(offer.city.latitude or 0)
                        )
                        # إضافة عامل عشوائي بسيط للمدن
                        distance += random.uniform(0, 5)
                        offers_with_distance.append({
                            'offer': offer,
                            'distance': distance
                        })
                
                # ترتيب حسب المسافة
                offers_with_distance.sort(key=lambda x: x['distance'])
                
                # أخذ أقرب 7 عروض
                nearby_offers = [item['offer'] for item in offers_with_distance[:7]]
                
                # إضافة المسافة للسيريالايزر
                serializer_data = []
                for item in offers_with_distance[:7]:
                    offer_data = OfferSerializer(item['offer'], context={'request': request}).data
                    offer_data['distance'] = round(item['distance'], 1)
                    serializer_data.append(offer_data)
                
                return Response({
                    'use_gps': True,
                    'offers': serializer_data
                })
                
            except (ValueError, TypeError):
                pass
        
        # الخيار الثاني: استخدام المدينة
        if user_city_id:
            offers = offers.filter(city_id=user_city_id)
        
        # أخذ آخر 7 عروض من المدينة
        offers = offers.order_by('-created_at')[:7]
        serializer = OfferSerializer(offers, many=True, context={'request': request})
        
        return Response({
            'use_gps': False,
            'city_based': True,
            'offers': serializer.data
        })




# ============= Online Users Settings View =============
class OnlineUsersSettingsView(APIView):
    '''API لجلب إعدادات المتواجدين'''
    permission_classes = [AllowAny]
    
    def get(self, request):
        settings, created = OnlineUsersSettings.objects.get_or_create(pk=1)
        serializer = OnlineUsersSettingsSerializer(settings)
        return Response(serializer.data)


class CheckAuthView(APIView):
    '''View للتحقق من حالة المصادقة - للتصحيح'''
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        '''التحقق من المصادقة'''
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'phone_number': getattr(request.user, 'phone_number', 'N/A'),
                'is_authenticated': request.user.is_authenticated
            },
            'auth_header': request.headers.get('Authorization', 'None'),
            'message': 'المصادقة تعمل بشكل صحيح'
        })
    
    def post(self, request):
        '''اختبار المصادقة مع POST'''
        return Response({
            'authenticated': True,
            'method': 'POST',
            'data_received': request.data,
            'user_id': request.user.id,
            'message': 'POST request authenticated successfully'
        })


# ============= Business Types View =============
class BusinessTypeListView(APIView):
    '''جلب قائمة أنواع الأنشطة التجارية'''
    permission_classes = [AllowAny]
    
    def get(self, request):
        business_types = BusinessType.objects.filter(is_active=True).order_by('order', 'name')
        data = [{'id': bt.id, 'name': bt.name, 'icon': bt.icon} for bt in business_types]
        return Response(data)
