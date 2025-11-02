from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models_notifications import FCMToken, Notification
from .fcm_service import FCMService


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_fcm_token(request):
    """حفظ FCM Token للمستخدم"""
    
    token = request.data.get('token')
    device_type = request.data.get('device_type', 'android')
    
    if not token:
        return Response(
            {'error': 'Token مطلوب'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # حفظ أو تحديث Token
    fcm_token, created = FCMToken.objects.update_or_create(
        user=request.user,
        defaults={
            'token': token,
            'device_type': device_type,
            'is_active': True
        }
    )
    
    return Response({
        'success': True,
        'message': 'تم حفظ Token بنجاح',
        'created': created
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_fcm_token(request):
    """حذف FCM Token (عند تسجيل الخروج)"""
    
    try:
        fcm_token = FCMToken.objects.get(user=request.user)
        fcm_token.is_active = False
        fcm_token.save()
        
        return Response({
            'success': True,
            'message': 'تم إلغاء تفعيل الإشعارات'
        })
    except FCMToken.DoesNotExist:
        return Response({
            'success': True,
            'message': 'لا يوجد Token لحذفه'
        })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def send_notification_admin(request):
    """إرسال إشعار من المدير (Admin Panel فقط)"""
    
    title = request.data.get('title')
    body = request.data.get('body')
    send_to_all = request.data.get('send_to_all', False)
    user_ids = request.data.get('user_ids', [])
    
    if not title or not body:
        return Response(
            {'error': 'Title و Body مطلوبان'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        if send_to_all:
            notification = FCMService.send_custom_notification(
                title=title,
                body=body,
                send_to_all=True
            )
        else:
            from users.models import CustomUser
            users = CustomUser.objects.filter(id__in=user_ids)
            notification = FCMService.send_custom_notification(
                title=title,
                body=body,
                target_users=users
            )
        
        return Response({
            'success': True,
            'message': 'تم إرسال الإشعار',
            'notification_id': notification.id,
            'sent_count': notification.sent_count,
            'success_count': notification.success_count,
            'failed_count': notification.failed_count
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def notifications_history(request):
    """عرض سجل الإشعارات (Admin فقط)"""
    
    notifications = Notification.objects.all()[:50]
    
    data = []
    for notif in notifications:
        data.append({
            'id': notif.id,
            'title': notif.title,
            'body': notif.body,
            'type': notif.get_notification_type_display(),
            'sent_to_all': notif.send_to_all,
            'sent_count': notif.sent_count,
            'success_count': notif.success_count,
            'failed_count': notif.failed_count,
            'sent_at': notif.sent_at,
            'created_at': notif.created_at
        })
    
    return Response(data)
