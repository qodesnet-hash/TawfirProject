"""
Firebase Phone Authentication
المصادقة عبر رقم الجوال باستخدام Firebase
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import logging
import firebase_admin
from firebase_admin import auth as firebase_auth

logger = logging.getLogger(__name__)
User = get_user_model()


class FirebasePhoneAuthView(APIView):
    """
    Firebase Phone Authentication
    التحقق من رقم الجوال عبر Firebase وإنشاء/تسجيل دخول المستخدم
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        firebase_token = request.data.get('firebase_token')
        
        if not firebase_token:
            return Response({
                'error': 'رمز Firebase مطلوب',
                'error_en': 'Firebase token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # التحقق من Firebase Token
            decoded_token = firebase_auth.verify_id_token(firebase_token)
            
            # استخراج رقم الجوال من التوكن
            phone_number = decoded_token.get('phone_number')
            firebase_uid = decoded_token.get('uid')
            
            if not phone_number:
                return Response({
                    'error': 'رقم الجوال غير موجود في التوكن',
                    'error_en': 'Phone number not found in token'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # تنظيف رقم الجوال (إزالة +967 وأي أصفار زائدة)
            clean_phone = phone_number.replace('+967', '').lstrip('0')
            
            logger.info(f"📱 Phone auth attempt: {phone_number} (clean: {clean_phone})")
            
            with transaction.atomic():
                # البحث عن المستخدم بالرقم أو إنشاء مستخدم جديد
                user = None
                created = False
                
                # البحث بالرقم المنظف
                user = User.objects.filter(phone_number=clean_phone).first()
                
                # البحث بالرقم الكامل مع كود الدولة
                if not user:
                    user = User.objects.filter(phone_number=phone_number).first()
                
                # البحث بـ Firebase UID
                if not user:
                    user = User.objects.filter(firebase_uid=firebase_uid).first()
                
                # إنشاء مستخدم جديد
                if not user:
                    # إنشاء إيميل وهمي من رقم الجوال
                    temp_email = f"{clean_phone}@tawfir.phone"
                    
                    user = User.objects.create(
                        email=temp_email,
                        phone_number=clean_phone,
                        firebase_uid=firebase_uid,
                        user_type='customer',
                        is_verified=True,
                    )
                    created = True
                    logger.info(f"✅ New user created: {clean_phone}")
                else:
                    # تحديث المستخدم الموجود
                    if not user.firebase_uid:
                        user.firebase_uid = firebase_uid
                    user.last_activity = timezone.now()
                    user.login_count = (user.login_count or 0) + 1
                    user.save()
                    logger.info(f"✅ User login: {clean_phone}")
                
                # إنشاء JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                # حفظ في OutstandingToken
                try:
                    from django.db import connection
                    jti = refresh.payload.get('jti')
                    exp = refresh.payload.get('exp')
                    
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """INSERT INTO token_blacklist_outstandingtoken 
                               (user_id, jti, token, created_at, expires_at) 
                               VALUES (%s, %s, %s, NOW(), to_timestamp(%s))
                               ON CONFLICT (jti) DO NOTHING""",
                            [user.id, jti, str(refresh), exp]
                        )
                except Exception as e:
                    logger.warning(f'⚠️ Could not save outstanding token: {e}')
                
                # التحقق إذا كان الملف الشخصي مكتمل
                needs_completion = user.needs_profile_completion
                
                return Response({
                    'success': True,
                    'access': access_token,
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'phone_number': user.phone_number,
                        'full_name': user.full_name,
                        'user_type': user.user_type,
                        'is_verified': user.is_verified,
                        'needs_profile_completion': needs_completion,
                        'city': user.city.id if user.city else None,
                        'city_name': user.city.name if user.city else None,
                        'latitude': str(user.latitude) if user.latitude else None,
                        'longitude': str(user.longitude) if user.longitude else None,
                        'address': user.address,
                    },
                    'is_new_user': created,
                    'message': 'تم تسجيل الدخول بنجاح' if not created else 'مرحباً بك في توفير!'
                })
                
        except firebase_admin.exceptions.FirebaseError as e:
            logger.error(f"Firebase auth error: {e}")
            return Response({
                'error': 'رمز Firebase غير صالح',
                'error_en': 'Invalid Firebase token',
                'details': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Phone auth error: {e}", exc_info=True)
            return Response({
                'error': 'حدث خطأ في تسجيل الدخول',
                'error_en': 'Login error',
                'details': str(e) if settings.DEBUG else 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompletePhoneProfileView(APIView):
    """
    إكمال الملف الشخصي بعد التسجيل برقم الجوال
    الحقول المطلوبة: الاسم + الموقع الجغرافي
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        data = request.data
        
        logger.info(f"📝 Profile completion for: {user.phone_number}")
        logger.info(f"📝 Data: {data}")
        
        try:
            # التحقق من الاسم
            if not data.get('full_name'):
                return Response({
                    'error': 'الاسم مطلوب',
                    'error_en': 'Name required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.full_name = data['full_name']
            
            # الموقع الجغرافي
            if data.get('latitude') and data.get('longitude'):
                user.latitude = data['latitude']
                user.longitude = data['longitude']
                logger.info(f"📍 Location: {user.latitude}, {user.longitude}")
            
            # العنوان (اختياري أو من Geocoding)
            if data.get('address'):
                user.address = data['address']
            
            # المدينة (اختيارية - يمكن تحديدها لاحقاً من الموقع)
            if data.get('city_id'):
                from api.models import City
                try:
                    city = City.objects.get(id=data['city_id'])
                    user.city = city
                    user.selected_city = city
                    logger.info(f"🏙️ City: {city.name}")
                except City.DoesNotExist:
                    logger.warning(f"City not found: {data['city_id']}")
            
            user.save()
            logger.info(f"✅ Profile completed for: {user.phone_number}")
            
            return Response({
                'success': True,
                'message': 'تم حفظ البيانات بنجاح',
                'user': {
                    'id': user.id,
                    'phone_number': user.phone_number,
                    'full_name': user.full_name,
                    'city': user.city.id if user.city else None,
                    'city_name': user.city.name if user.city else None,
                    'latitude': str(user.latitude) if user.latitude else None,
                    'longitude': str(user.longitude) if user.longitude else None,
                    'address': user.address,
                    'needs_profile_completion': user.needs_profile_completion
                }
            })
            
        except Exception as e:
            logger.error(f"Profile completion error: {e}", exc_info=True)
            return Response({
                'error': 'حدث خطأ في حفظ البيانات',
                'error_en': 'Save error',
                'details': str(e) if settings.DEBUG else 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_phone_exists(request):
    """
    التحقق إذا كان رقم الجوال مسجل مسبقاً
    """
    phone_number = request.data.get('phone_number', '')
    
    # تنظيف الرقم
    clean_phone = phone_number.replace('+967', '').replace(' ', '').lstrip('0')
    
    exists = User.objects.filter(phone_number=clean_phone).exists()
    
    if not exists:
        # البحث بالرقم الكامل أيضاً
        exists = User.objects.filter(phone_number=phone_number).exists()
    
    return Response({
        'exists': exists,
        'phone_number': clean_phone
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_phone_profile(request):
    """
    جلب بيانات المستخدم المسجل برقم الجوال
    """
    user = request.user
    
    return Response({
        'success': True,
        'user': {
            'id': user.id,
            'phone_number': user.phone_number,
            'full_name': user.full_name,
            'user_type': user.user_type,
            'is_verified': user.is_verified,
            'city': user.city.id if user.city else None,
            'city_name': user.city.name if user.city else None,
            'latitude': str(user.latitude) if user.latitude else None,
            'longitude': str(user.longitude) if user.longitude else None,
            'address': user.address,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'needs_profile_completion': user.needs_profile_completion
        }
    })
