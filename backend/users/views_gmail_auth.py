"""
SECURE Google Authentication
المصادقة الآمنة عبر Google مع التحقق الكامل
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

# ══════════════════════════════════════════════════════════════════
# IMPORTANT: Install google-auth library
# pip install google-auth --break-system-packages
# ══════════════════════════════════════════════════════════════════

try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    logging.warning("google-auth not installed! Google token verification disabled!")

logger = logging.getLogger(__name__)
User = get_user_model()

GOOGLE_CLIENT_ID = getattr(settings, 'GOOGLE_CLIENT_ID', 
                           '409608657151-95dqok74ojre9b6u377f1vsritt6afb3.apps.googleusercontent.com')


def verify_google_token(token_str):
    """
    التحقق من صحة Google ID Token
    Verify Google ID Token authenticity
    
    Returns: (is_valid, payload_or_error)
    """
    if not GOOGLE_AUTH_AVAILABLE:
        logger.error("Google auth library not available!")
        return False, "Google authentication library not installed"
    
    try:
        # التحقق من التوكن مع Google
        idinfo = id_token.verify_oauth2_token(
            token_str, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # التحقق من المُصدر
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            logger.warning(f"Invalid token issuer: {idinfo['iss']}")
            return False, "Invalid token issuer"
        
        # التحقق من audience (client ID)
        if idinfo['aud'] != GOOGLE_CLIENT_ID:
            logger.warning(f"Invalid audience: {idinfo['aud']}")
            return False, "Invalid token audience"
        
        return True, idinfo
        
    except ValueError as e:
        logger.error(f"Invalid token: {str(e)}")
        return False, f"Invalid token: {str(e)}"
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return False, f"Verification error: {str(e)}"


class GoogleAuthView(APIView):
    """
    Secure Google Authentication with token verification
    """
    permission_classes = [AllowAny]
    throttle_scope = 'auth'  # 10 requests/minute
    
    def post(self, request):
        id_token_str = request.data.get('id_token')
        user_type = request.data.get('user_type', 'customer')
        
        if not id_token_str:
            return Response({
                'error': 'رمز Google مطلوب',
                'error_en': 'Google token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ══════════════════════════════════════════════════════════
        # SECURITY: Verify Google Token
        # ══════════════════════════════════════════════════════════
        
        is_valid, result = verify_google_token(id_token_str)
        
        if not is_valid:
            logger.warning(f"Invalid Google token attempt: {result}")
            return Response({
                'error': 'رمز Google غير صالح',
                'error_en': 'Invalid Google token',
                'details': str(result)
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # استخراج البيانات من التوكن المُتحقق منه
        google_payload = result
        email = google_payload.get('email')
        full_name = google_payload.get('name', '')
        google_id = google_payload.get('sub')  # Google User ID
        email_verified = google_payload.get('email_verified', False)
        
        if not email:
            return Response({
                'error': 'البريد الإلكتروني مطلوب',
                'error_en': 'Email required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not email_verified:
            logger.warning(f"Unverified email attempt: {email}")
            return Response({
                'error': 'البريد الإلكتروني غير موثق من Google',
                'error_en': 'Email not verified by Google'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # البحث أو إنشاء المستخدم
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'google_id': google_id,
                        'full_name': full_name,
                        'user_type': user_type,
                        'is_verified': True,
                    }
                )
                
                if not created:
                    # تحديث المستخدم الموجود
                    if not user.google_id:
                        user.google_id = google_id
                    if not user.full_name and full_name:
                        user.full_name = full_name
                    user.last_activity = timezone.now()
                    user.login_count = (user.login_count or 0) + 1
                    user.save()
                    
                    logger.info(f"User login: {email}")
                else:
                    logger.info(f"New user registered: {email}")
                
                # إنشاء JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                needs_completion = user.needs_profile_completion
                
                # إنشاء طلب تاجر إذا لزم الأمر
                if created and user_type == 'merchant':
                    try:
                        from api.models import MerchantRequest
                        MerchantRequest.objects.create(
                            user=user, 
                            business_name=full_name or email,
                            status='pending'
                        )
                        logger.info(f"Merchant request created for: {email}")
                    except Exception as e:
                        logger.error(f"Could not create merchant request: {e}")
                
                return Response({
                    'success': True,
                    'access': access_token,
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'user_type': user.user_type,
                        'is_verified': user.is_verified,
                        'is_merchant_verified': user.is_verified_merchant,
                        'needs_profile_completion': needs_completion,
                        'city': user.city.id if user.city else None,
                        'phone_number': user.phone_number,
                    },
                    'is_new_user': created,
                    'message': 'تم تسجيل الدخول بنجاح' if not created else 'مرحباً بك في توفير!'
                })
                
        except Exception as e:
            logger.error(f"Google auth error for {email}: {e}", exc_info=True)
            return Response({
                'error': 'حدث خطأ في تسجيل الدخول',
                'error_en': 'Login error',
                'details': str(e) if settings.DEBUG else 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompleteProfileView(APIView):
    """
    FIXED: Now requires authentication!
    """
    permission_classes = [IsAuthenticated]  # ✅ FIXED!
    
    def post(self, request):
        user = request.user  # ✅ من المستخدم المصادق عليه
        
        logger.info(f"Profile completion attempt for user: {user.email}")
        
        data = request.data
        
        try:
            # التحقق من الحقول المطلوبة
            if not data.get('phone_number'):
                return Response({
                    'error': 'رقم الجوال مطلوب',
                    'error_en': 'Phone number required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not data.get('city_id'):
                return Response({
                    'error': 'المدينة مطلوبة',
                    'error_en': 'City required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # تحديث الاسم
            if data.get('full_name'):
                user.full_name = data['full_name']
            
            # التحقق من رقم الهاتف
            phone = data['phone_number']
            if phone.startswith('0'):
                phone = phone[1:]
            
            # التحقق من عدم تكرار رقم الهاتف
            if User.objects.exclude(id=user.id).filter(phone_number=phone).exists():
                return Response({
                    'error': 'رقم الجوال مستخدم بالفعل',
                    'error_en': 'Phone number already in use'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.phone_number = phone
            
            # تحديث المدينة
            from api.models import City
            try:
                city = City.objects.get(id=data['city_id'])
                user.city = city
            except City.DoesNotExist:
                return Response({
                    'error': 'المدينة غير موجودة',
                    'error_en': 'City not found'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # حقول اختيارية
            if data.get('date_of_birth'):
                user.date_of_birth = data['date_of_birth']
            
            if data.get('address'):
                user.address = data['address']
            
            user.save()
            
            logger.info(f"Profile completed successfully for: {user.email}")
            
            # تحديث طلب التاجر إن وجد
            if user.is_merchant:
                try:
                    from api.models import MerchantRequest
                    merchant_request = MerchantRequest.objects.filter(user=user).first()
                    if merchant_request:
                        merchant_request.phone = user.phone_number
                        merchant_request.address = user.address or ''
                        merchant_request.save()
                except Exception as e:
                    logger.error(f"Could not update merchant request: {e}")
            
            return Response({
                'success': True,
                'message': 'تم تحديث البيانات بنجاح',
                'message_en': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'phone_number': user.phone_number,
                    'city': {'id': user.city.id, 'name': user.city.name} if user.city else None,
                    'user_type': user.user_type,
                    'profile_complete': not user.needs_profile_completion
                }
            })
            
        except Exception as e:
            logger.error(f"Profile completion error for {user.email}: {e}", exc_info=True)
            return Response({
                'error': 'حدث خطأ في تحديث البيانات',
                'error_en': 'Update error',
                'details': str(e) if settings.DEBUG else 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateMerchantLocationView(APIView):
    """
    FIXED: Now requires authentication!
    """
    permission_classes = [IsAuthenticated]  # ✅ FIXED!
    
    def post(self, request):
        user = request.user  # ✅ من المستخدم المصادق عليه
        
        if not user.is_merchant:
            return Response({
                'error': 'هذه الخدمة للتجار فقط',
                'error_en': 'Merchants only'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            from api.models import Merchant
            
            merchant, created = Merchant.objects.get_or_create(
                user=user,
                defaults={'business_name': user.full_name or user.email}
            )
            
            # تحديث الموقع
            merchant.latitude = request.data.get('latitude')
            merchant.longitude = request.data.get('longitude')
            
            if request.data.get('address'):
                merchant.address = request.data['address']
                user.address = request.data['address']
                user.save()
            
            merchant.save()
            
            logger.info(f"Merchant location updated: {user.email}")
            
            return Response({
                'success': True,
                'message': 'تم تحديث موقع المتجر بنجاح',
                'message_en': 'Location updated successfully',
                'location': {
                    'latitude': merchant.latitude,
                    'longitude': merchant.longitude,
                    'address': merchant.address
                }
            })
            
        except Exception as e:
            logger.error(f"Location update error for {user.email}: {e}", exc_info=True)
            return Response({
                'error': 'حدث خطأ في تحديث الموقع',
                'error_en': 'Update error',
                'details': str(e) if settings.DEBUG else 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    جلب بيانات المستخدم - يتطلب مصادقة
    """
    user = request.user
    
    return Response({
        'success': True,
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'phone_number': user.phone_number,
            'user_type': user.user_type,
            'is_verified': user.is_verified,
            'merchant_verified': user.merchant_verified,
            'is_merchant_verified': user.is_verified_merchant,
            'city': {'id': user.city.id, 'name': user.city.name} if user.city else None,
            'needs_profile_completion': user.needs_profile_completion,
            'address': user.address,
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def check_profile_status(request):
    """
    التحقق من حالة الملف الشخصي - لا يتطلب مصادقة
    """
    email = request.GET.get('email')
    if not email:
        return Response({
            'error': 'Email مطلوب',
            'error_en': 'Email required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'المستخدم غير موجود',
            'error_en': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    missing_fields = []
    if not user.full_name:
        missing_fields.append('full_name')
    if not user.phone_number:
        missing_fields.append('phone_number')
    if not user.city:
        missing_fields.append('city')
    
    if user.is_merchant:
        try:
            from api.models import Merchant
            merchant = Merchant.objects.filter(user=user).first()
            if not merchant or not merchant.latitude or not merchant.longitude:
                missing_fields.append('location')
        except:
            missing_fields.append('location')
    
    return Response({
        'profile_complete': len(missing_fields) == 0,
        'missing_fields': missing_fields,
        'user_type': user.user_type,
        'is_verified': user.is_verified,
        'is_merchant_verified': user.is_verified_merchant if user.is_merchant else None
    })
