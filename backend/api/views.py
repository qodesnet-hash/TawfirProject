from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, F
from django.db import models
from .models import Offer, City, Favorite, Merchant, Review, OnlineUsersSettings
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
    queryset = City.objects.filter(is_active=True)
    serializer_class = CitySerializer
    permission_classes = [AllowAny]

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
        offer = get_object_or_404(Offer, pk=offer_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            offer=offer
        )
        
        if not created:
            favorite.delete()
            return Response({'status': 'removed', 'message': 'تم إزالة العرض من المفضلة'})
        
        return Response({'status': 'added', 'message': 'تم إضافة العرض إلى المفضلة'})

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
        print(f"ReviewCreateView - User: {request.user}")
        print(f"ReviewCreateView - Is authenticated: {request.user.is_authenticated}")
        print(f"ReviewCreateView - Request data: {request.data}")
        print(f"ReviewCreateView - Auth header: {request.headers.get('Authorization', 'None')}")
        
        # التحقق من المصادقة بشكل صريح
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'يجب تسجيل الدخول أولاً', 'detail': 'Authentication credentials were not provided.'},
                status=401
            )
        
        # التحقق من وجود المتجر
        try:
            merchant = Merchant.objects.get(pk=merchant_id)
        except Merchant.DoesNotExist:
            return Response(
                {'error': 'المتجر غير موجود', 'merchant_id': merchant_id},
                status=404
            )
        
        # التحقق من وجود تقييم سابق
        existing_review = Review.objects.filter(user=request.user, merchant=merchant).first()
        
        if existing_review:
            # تحديث التقييم الموجود بدلاً من إرجاع خطأ
            print(f"Found existing review ID={existing_review.id}, updating instead of creating")
            serializer = ReviewCreateSerializer(existing_review, data=request.data, partial=True)
            
            if serializer.is_valid():
                updated_review = serializer.save()
                print(f"✅ Review updated successfully: ID={updated_review.id}")
                response_serializer = ReviewSerializer(updated_review)
                return Response(
                    {
                        'message': 'تم تحديث التقييم بنجاح',
                        'action': 'updated',
                        'review': response_serializer.data
                    }, 
                    status=200  # نستخدم 200 للتحديث
                )
            else:
                print(f"Validation errors during update: {serializer.errors}")
                return Response(
                    {
                        'error': 'البيانات المرسلة غير صحيحة',
                        'details': serializer.errors
                    },
                    status=400
                )
        else:
            # إنشاء تقييم جديد
            serializer = ReviewCreateSerializer(data=request.data)
            if serializer.is_valid():
                # حفظ التقييم
                try:
                    review = serializer.save(
                        user=request.user, 
                        merchant=merchant,
                        comment=serializer.validated_data.get('comment', '')
                    )
                    # إرجاع البيانات باستخدام ReviewSerializer
                    response_serializer = ReviewSerializer(review)
                    print(f"✅ Review created successfully for user {request.user.phone_number} on merchant {merchant_id}")
                    return Response(
                        {
                            'message': 'تم إضافة التقييم بنجاح',
                            'action': 'created',
                            'review': response_serializer.data
                        },
                        status=201
                    )
                except Exception as e:
                    print(f"Error saving review: {str(e)}")
                    return Response(
                        {'error': f'حدث خطأ في حفظ المراجعة: {str(e)}'},
                        status=500
                    )
            else:
                print(f"Validation errors: {serializer.errors}")
                return Response(
                    {
                        'error': 'البيانات المرسلة غير صحيحة',
                        'details': serializer.errors,
                        'hint': 'تأكد من أن التقييم بين 1 و 5'
                    },
                    status=400
                )

class ReviewUpdateView(APIView):
    """تحديث تقييم موجود"""
    permission_classes = [IsAuthenticated]
    
    def put(self, request, merchant_id):
        print(f"ReviewUpdateView PUT - User: {request.user}")
        print(f"ReviewUpdateView PUT - Merchant ID: {merchant_id}")
        print(f"ReviewUpdateView PUT - Data: {request.data}")
        
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
        
        # تحديث المراجعة
        serializer = ReviewCreateSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            updated_review = serializer.save()
            print(f"Review updated: ID={updated_review.id}, New Rating={updated_review.rating}, New Comment={updated_review.comment}")
            response_serializer = ReviewSerializer(updated_review)
            return Response(
                {
                    'message': 'تم تحديث التقييم بنجاح',
                    'review': response_serializer.data
                },
                status=200
            )
        else:
            print(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=400)
    
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
