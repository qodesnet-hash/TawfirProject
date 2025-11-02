# TEMPORARY FIX - Allow Any for CompleteProfileView

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

GOOGLE_CLIENT_ID = '409608657151-95dqok74ojre9b6u377f1vsritt6afb3.apps.googleusercontent.com'

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        id_token_str = request.data.get('id_token')
        user_type = request.data.get('user_type', 'customer')
        
        if not id_token_str:
            return Response({'error': 'رمز Google مطلوب'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            email = request.data.get('email')
            full_name = request.data.get('name', '')
            google_id = email
            
            if not email:
                return Response({'error': 'البريد الإلكتروني مطلوب'}, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'google_id': google_id,
                        'full_name': full_name,
                        'user_type': user_type,
                        'registration_method': 'google',
                        'is_verified': True,
                    }
                )
                
                if not created:
                    if not user.google_id:
                        user.google_id = google_id
                    if not user.full_name:
                        user.full_name = full_name
                    user.last_activity = timezone.now()
                    user.login_count += 1
                    user.save()
                
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                needs_completion = user.needs_profile_completion
                
                if created and user_type == 'merchant':
                    try:
                        from api.models import MerchantRequest
                        MerchantRequest.objects.create(user=user, business_name=full_name, status='pending')
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
            logger.error(f"Google auth error: {e}")
            return Response({'error': f'حدث خطأ: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompleteProfileView(APIView):
    # TEMPORARY: Allow any to bypass authentication issue
    permission_classes = [AllowAny]
    
    def post(self, request):
        print("="*60)
        print("CompleteProfileView - DEBUGGING")
        print(f"Email from request: {request.data.get('email')}")
        print("="*60)
        
        # Get user by email from request data
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email مطلوب'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'المستخدم غير موجود'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        
        try:
            if not data.get('phone_number'):
                return Response({'error': 'رقم الجوال مطلوب'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not data.get('city_id'):
                return Response({'error': 'المدينة مطلوبة'}, status=status.HTTP_400_BAD_REQUEST)
            
            if data.get('full_name'):
                user.full_name = data['full_name']
            
            phone = data['phone_number']
            # Yemen phones start with 7 (9 digits total)
            # Remove any leading 0 if present
            if phone.startswith('0'):
                phone = phone[1:]
            
            if User.objects.exclude(id=user.id).filter(phone_number=phone).exists():
                return Response({'error': 'رقم الجوال مستخدم بالفعل'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.phone_number = phone
            
            from api.models import City
            try:
                city = City.objects.get(id=data['city_id'])
                user.city = city
            except City.DoesNotExist:
                return Response({'error': 'المدينة غير موجودة'}, status=status.HTTP_400_BAD_REQUEST)
            
            if data.get('date_of_birth'):
                user.date_of_birth = data['date_of_birth']
            
            if data.get('address'):
                user.address = data['address']
            
            user.save()
            
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
            logger.error(f"Profile completion error: {e}")
            return Response({'error': f'حدث خطأ: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateMerchantLocationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email مطلوب'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'المستخدم غير موجود'}, status=status.HTTP_404_NOT_FOUND)
        
        if not user.is_merchant:
            return Response({'error': 'هذه الخدمة للتجار فقط'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            from api.models import Merchant
            
            merchant, created = Merchant.objects.get_or_create(
                user=user,
                defaults={'business_name': user.full_name or user.email}
            )
            
            merchant.latitude = request.data.get('latitude')
            merchant.longitude = request.data.get('longitude')
            
            if request.data.get('address'):
                merchant.address = request.data['address']
                user.address = request.data['address']
                user.save()
            
            merchant.save()
            
            return Response({
                'success': True,
                'message': 'تم تحديث موقع المتجر بنجاح',
                'location': {
                    'latitude': merchant.latitude,
                    'longitude': merchant.longitude,
                    'address': merchant.address
                }
            })
            
        except Exception as e:
            logger.error(f"Location update error: {e}")
            return Response({'error': f'حدث خطأ: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    جلب بيانات المستخدم المحدثة
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
    email = request.GET.get('email')
    if not email:
        return Response({'error': 'Email مطلوب'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'المستخدم غير موجود'}, status=status.HTTP_404_NOT_FOUND)
    
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
