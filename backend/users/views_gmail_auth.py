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
        user_type = 'customer'  # جميع المستخدمين الجدد يسجلون كـ customer
        dev_mode = request.data.get('dev_mode', False)  # 🚀 وضع التطوير
        
        if not id_token_str:
            return Response({
                'error': 'رمز Google مطلوب',
                'error_en': 'Google token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ══════════════════════════════════════════════════════════
        # 🚀 DEVELOPMENT MODE: تخطي التحقق من Google Token
        # ══════════════════════════════════════════════════════════
        if dev_mode and settings.DEBUG:
            logger.warning("⚠️ DEV MODE: Skipping Google token verification")
            email = request.data.get('email')
            full_name = request.data.get('name', 'Dev User')
            google_id = f"dev_{email}_{timezone.now().timestamp()}"
            email_verified = True
        else:
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
        
        if not email_verified and not dev_mode:
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
                
                # ✅ حفظ في OutstandingToken
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
                    logger.info(f'✅ Outstanding token saved for {user.email}')
                except Exception as e:
                    logger.warning(f'⚠️ Could not save outstanding token: {e}')
                
                needs_completion = user.needs_profile_completion

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
        
        logger.info(f"📝 Profile completion attempt for user: {user.email}")
        logger.info(f"📝 Received data: {request.data}")
        
        data = request.data
        
        try:
            # التحقق من الحقول المطلوبة
            if not data.get('phone_number'):
                logger.warning('⚠️ Missing phone_number')
                return Response({
                    'error': 'رقم الجوال مطلوب',
                    'error_en': 'Phone number required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not data.get('city_id'):
                logger.warning('⚠️ Missing city_id')
                return Response({
                    'error': 'المدينة مطلوبة',
                    'error_en': 'City required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # تحديث الاسم
            if data.get('full_name'):
                user.full_name = data['full_name']
                logger.info(f"✅ Updated full_name: {user.full_name}")
            
            # التحقق من رقم الهاتف
            phone = data['phone_number']
            if phone.startswith('0'):
                phone = phone[1:]
            
            logger.info(f"📱 Processing phone: {phone}")
            
            # التحقق من عدم تكرار رقم الهاتف
            if User.objects.exclude(id=user.id).filter(phone_number=phone).exists():
                logger.warning(f'⚠️ Phone number already exists: {phone}')
                return Response({
                    'error': 'رقم الجوال مستخدم بالفعل',
                    'error_en': 'Phone number already in use'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.phone_number = phone
            
            # تحديث المدينة
            from api.models import City
            try:
                city_id = int(data['city_id'])
                logger.info(f"🏙️ Looking for city ID: {city_id}")
                city = City.objects.get(id=city_id)
                user.city = city
                logger.info(f"✅ City set: {city.name}")
            except ValueError:
                logger.error(f'❌ Invalid city_id format: {data["city_id"]}')
                return Response({
                    'error': 'رقم المدينة غير صحيح',
                    'error_en': 'Invalid city ID format'
                }, status=status.HTTP_400_BAD_REQUEST)
            except City.DoesNotExist:
                logger.error(f'❌ City not found: {city_id}')
                return Response({
                    'error': 'المدينة غير موجودة',
                    'error_en': 'City not found'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # حقول اختيارية
            if data.get('date_of_birth'):
                try:
                    # تحويل ISO format إلى date only
                    from datetime import datetime
                    date_str = data['date_of_birth']
                    if 'T' in date_str:  # ISO format
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        user.date_of_birth = date_obj.date()  # استخدام date فقط
                    else:
                        user.date_of_birth = date_str
                    logger.info(f"📅 Updated date_of_birth: {user.date_of_birth}")
                except Exception as e:
                    logger.warning(f"⚠️ Invalid date format: {data['date_of_birth']}, error: {e}")
            
            if data.get('address'):
                user.address = data['address']
                logger.info(f"🏠 Updated address: {user.address}")
            
            if data.get('latitude'):
                user.latitude = data['latitude']
                logger.info(f"📍 Updated latitude: {user.latitude}")
            
            if data.get('longitude'):
                user.longitude = data['longitude']
                logger.info(f"📍 Updated longitude: {user.longitude}")
            
            user.save()
            logger.info(f"✅✅✅ Profile saved successfully for: {user.email}")
            
            # تحديث طلب التاجر إن وجد
            if user.is_merchant:
                try:
                    from api.models import MerchantRequest
                    merchant_request = MerchantRequest.objects.filter(user=user).first()
                    if merchant_request:
                        merchant_request.phone = user.phone_number
                        merchant_request.address = user.address or ''
                        merchant_request.save()
                        logger.info(f"✅ Merchant request updated")
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
            logger.error(f"❌❌❌ Profile completion error for {user.email}: {e}", exc_info=True)
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
            'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'user_type': user.user_type,
            'is_verified': user.is_verified,
            'merchant_verified': user.merchant_verified,
            'is_merchant_verified': user.is_verified_merchant,
            'city': {'id': user.city.id, 'name': user.city.name} if user.city else None,
            'needs_profile_completion': user.needs_profile_completion,
            'address': user.address,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):
    """
    رفع صورة الملف الشخصي مع الضغط التلقائي
    """
    user = request.user
    
    # دعم كلا الطريقتين: FormData و base64
    if 'profile_picture' in request.FILES:
        # طريقة FormData التقليدية
        profile_picture_file = request.FILES['profile_picture']
    elif 'profile_picture_base64' in request.data:
        # طريقة base64
        import base64
        from django.core.files.base import ContentFile
        
        try:
            base64_data = request.data['profile_picture_base64']
            image_data = base64.b64decode(base64_data)
            profile_picture_file = ContentFile(image_data, name='profile.jpg')
        except Exception as e:
            logger.error(f'Error decoding base64: {e}')
            return Response({
                'error': 'خطأ في معالجة الصورة',
                'error_en': 'Error processing image'
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'error': 'الصورة مطلوبة',
            'error_en': 'Profile picture required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # ضغط الصورة قبل الحفظ
        from .image_utils import compress_profile_picture
        
        original_size = profile_picture_file.size
        logger.info(f'Original image size: {original_size / 1024:.2f} KB')
        
        compressed_file = compress_profile_picture(profile_picture_file)
        compressed_size = compressed_file.size if hasattr(compressed_file, 'size') else 0
        
        logger.info(f'Compressed image size: {compressed_size / 1024:.2f} KB')
        logger.info(f'Compression ratio: {(1 - compressed_size/original_size) * 100:.1f}%')
        
        # حذف الصورة القديمة إن وجدت
        if user.profile_picture:
            try:
                import os
                if os.path.isfile(user.profile_picture.path):
                    os.remove(user.profile_picture.path)
                    logger.info(f'Deleted old profile picture: {user.profile_picture.path}')
            except Exception as e:
                logger.warning(f'Could not delete old picture: {e}')
        
        # حفظ الصورة المضغوطة
        user.profile_picture = compressed_file
        user.save()
        
        logger.info(f'✅ Compressed profile picture saved for user: {user.email}')
        
        return Response({
            'success': True,
            'message': 'تم رفع الصورة بنجاح',
            'message_en': 'Profile picture uploaded successfully',
            'profile_picture': user.profile_picture.url,
            'original_size_kb': round(original_size / 1024, 2),
            'compressed_size_kb': round(compressed_size / 1024, 2) if compressed_size else 0
        })
        
    except Exception as e:
        logger.error(f'Error uploading profile picture: {e}', exc_info=True)
        return Response({
            'error': 'حدث خطأ في رفع الصورة',
            'error_en': 'Upload error',
            'details': str(e) if settings.DEBUG else 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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



@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    🚪 Logout - Blacklist the refresh token
    """
    refresh_token = request.data.get('refresh_token')
    
    # حاول الحصول على user من token
    user_email = "Unknown"
    try:
        if request.user.is_authenticated:
            user_email = request.user.email
    except:
        pass
    
    print(f'🚪 Logout for: {user_email}')  # ✅ print بدلاً من logger
    
    if not refresh_token:
        return Response({'success': True, 'message': 'تم تسجيل الخروج'})
    
    try:
        from django.db import connection
        
        token = RefreshToken(refresh_token)
        jti = token.payload.get('jti')
        print(f'🔑 JTI: {jti}')
        
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM token_blacklist_outstandingtoken WHERE jti = %s LIMIT 1",
                [jti]
            )
            row = cursor.fetchone()
            
            if row:
                outstanding_id = row[0]
                print(f'🔍 Found outstanding token: {outstanding_id}')
                
                cursor.execute(
                    "INSERT INTO token_blacklist_blacklistedtoken (token_id, blacklisted_at) VALUES (%s, NOW()) ON CONFLICT DO NOTHING",
                    [outstanding_id]
                )
                print(f'✅ Token blacklisted!')
            else:
                print(f'⚠️ Outstanding token not found')
        
        return Response({'success': True, 'message': 'تم تسجيل الخروج بنجاح'})
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        print(traceback.format_exc())
        return Response({'success': True, 'message': 'تم تسجيل الخروج'})


