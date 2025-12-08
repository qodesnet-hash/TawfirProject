"""
خدمة إرسال الإشعارات عبر Firebase Admin SDK
"""
import firebase_admin
from firebase_admin import credentials, messaging
from .models_notifications import FCMToken, Notification
from django.utils import timezone
import os
from django.conf import settings


class FCMService:
    """خدمة إرسال الإشعارات باستخدام Firebase Admin SDK"""
    
    _initialized = False
    
    @classmethod
    def initialize_firebase(cls):
        """تهيئة Firebase Admin SDK مرة واحدة فقط"""
        if not cls._initialized:
            try:
                cred_path = os.path.join(settings.BASE_DIR, 'serviceAccountKey.json')
                
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    cls._initialized = True
                    print("✅ Firebase Admin SDK initialized successfully")
                else:
                    print(f"❌ serviceAccountKey.json not found at: {cred_path}")
            except ValueError as e:
                if "already exists" in str(e):
                    cls._initialized = True
                else:
                    raise
            except Exception as e:
                print(f"❌ Error initializing Firebase: {str(e)}")
    
    @classmethod
    def send_to_token(cls, token, title, body, data=None, image_url=None):
        """إرسال إشعار لتوكن واحد
        
        Args:
            token: FCM token
            title: عنوان الإشعار
            body: نص الإشعار
            data: بيانات إضافية
            image_url: رابط صورة الإشعار (Big Picture)
        """
        cls.initialize_firebase()
        
        if not cls._initialized:
            print("❌ Firebase not initialized. Cannot send notification.")
            return False
        
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"SENDING NOTIFICATION - image_url: {image_url}")
        
        try:
            # إضافة الصورة للـ data
            notification_data = {}
            if data:
                for key, value in data.items():
                    notification_data[key] = str(value)
            if image_url:
                notification_data['image'] = image_url
                notification_data['imageUrl'] = image_url
                notification_data['bigPicture'] = image_url
            
            # إعداد Android مع الصورة الكبيرة
            android_notification = messaging.AndroidNotification(
                title=title,
                body=body,
                color='#10B981',
                sound='default',
                default_sound=True,
                visibility='public',
                image=image_url if image_url else None,
            )
            
            android_config = messaging.AndroidConfig(
                priority='high',
                notification=android_notification,
            )
            
            # إعداد iOS
            apns_config = None
            if image_url:
                apns_config = messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            mutable_content=True,
                            sound='default',
                        ),
                    ),
                    fcm_options=messaging.APNSFCMOptions(
                        image=image_url,
                    ),
                )
            
            # الإشعار الرئيسي
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url if image_url else None,
            )
            
            message = messaging.Message(
                notification=notification,
                data=notification_data,
                token=token,
                android=android_config,
                apns=apns_config,
            )
            
            response = messaging.send(message)
            logger.warning(f"SUCCESS - Message sent: {response}")
            return True
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"ERROR sending notification: {str(e)}")
            return False
    
    @classmethod
    def send_to_user(cls, user, title, body, data=None):
        """إرسال إشعار لمستخدم واحد"""
        try:
            fcm_token = FCMToken.objects.get(user=user, is_active=True)
            return cls.send_to_token(fcm_token.token, title, body, data)
        except FCMToken.DoesNotExist:
            print(f"⚠️ لا يوجد FCM Token للمستخدم: {user.email}")
            return False
    
    @classmethod
    def send_to_all_users(cls, title, body, data=None):
        """إرسال إشعار لجميع المستخدمين"""
        tokens = FCMToken.objects.filter(is_active=True)
        success_count = 0
        failed_count = 0
        
        for fcm_token in tokens:
            if cls.send_to_token(fcm_token.token, title, body, data):
                success_count += 1
            else:
                failed_count += 1
        
        return {
            'total': tokens.count(),
            'success': success_count,
            'failed': failed_count
        }
    
    @classmethod
    def send_new_offer_notification(cls, offer):
        """إرسال إشعار عند إضافة عرض جديد"""
        title = "عرض جديد! 🎉"
        body = f"{offer.merchant.business_name}: {offer.title}"
        
        data = {
            "type": "new_offer",
            "offer_id": str(offer.id),
            "click_action": "OPEN_OFFER_DETAIL"
        }
        
        result = cls.send_to_all_users(title, body, data)
        
        notification = Notification.objects.create(
            title=title,
            body=body,
            notification_type='new_offer',
            offer=offer,
            send_to_all=True,
            sent_count=result['total'],
            success_count=result['success'],
            failed_count=result['failed'],
            sent_at=timezone.now()
        )
        
        return notification
    
    @classmethod
    def send_merchant_approved_notification(cls, merchant):
        """إرسال إشعار عند قبول التاجر"""
        title = "تم قبول طلبك! ✅"
        body = f"مبروك! تم قبول طلبك كتاجر. يمكنك الآن إضافة عروضك"
        
        data = {
            "type": "merchant_approved",
            "click_action": "OPEN_MERCHANT_DASHBOARD"
        }
        
        return cls.send_to_user(merchant.user, title, body, data)
    
    @classmethod
    def send_custom_notification(cls, title, body, target_users=None, send_to_all=False):
        """إرسال إشعار مخصص من المدير"""
        data = {
            "type": "general",
            "click_action": "OPEN_APP"
        }
        
        if send_to_all:
            result = cls.send_to_all_users(title, body, data)
        else:
            success_count = 0
            failed_count = 0
            for user in target_users:
                if cls.send_to_user(user, title, body, data):
                    success_count += 1
                else:
                    failed_count += 1
            result = {
                'total': len(target_users),
                'success': success_count,
                'failed': failed_count
            }
        
        notification = Notification.objects.create(
            title=title,
            body=body,
            notification_type='general',
            send_to_all=send_to_all,
            sent_count=result['total'],
            success_count=result['success'],
            failed_count=result['failed'],
            sent_at=timezone.now()
        )
        
        if not send_to_all:
            notification.target_users.set(target_users)
        
        return notification


# دالة مختصرة للاستخدام في views
def send_push_notification(token, title, body, data=None, image_url=None):
    """دالة مختصرة لإرسال إشعار لتوكن واحد
    
    Args:
        token: FCM token
        title: عنوان الإشعار
        body: نص الإشعار
        data: بيانات إضافية
        image_url: رابط صورة العرض (Big Picture Notification)
    """
    return FCMService.send_to_token(token, title, body, data, image_url)
