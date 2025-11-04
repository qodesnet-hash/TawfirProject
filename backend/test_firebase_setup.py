"""
اختبار إعداد Firebase Admin SDK
يتحقق من أن كل شيء معد بشكل صحيح
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings_simple')
django.setup()

from api.fcm_service import FCMService

def test_firebase_setup():
    """اختبار إعداد Firebase"""
    
    print("=" * 60)
    print("  اختبار إعداد Firebase Admin SDK")
    print("=" * 60)
    print()
    
    print("📋 الاختبارات:")
    print()
    
    # Test 1: Firebase Initialization
    print("1. اختبار تهيئة Firebase...")
    try:
        FCMService.initialize_firebase()
        if FCMService._initialized:
            print("   ✅ تم تهيئة Firebase بنجاح")
        else:
            print("   ❌ فشل تهيئة Firebase")
            print("   ⚠️  تحقق من وجود: serviceAccountKey.json")
            return
    except Exception as e:
        print(f"   ❌ خطأ: {str(e)}")
        return
    
    print()
    
    # Test 2: Check Models
    print("2. اختبار Models...")
    try:
        from api.models_notifications import FCMToken, Notification
        print("   ✅ Models موجودة")
    except Exception as e:
        print(f"   ❌ خطأ في Models: {str(e)}")
        return
    
    print()
    
    # Test 3: Check Admin
    print("3. اختبار Admin Panel...")
    try:
        from api.admin_notifications import FCMTokenAdmin, NotificationAdmin
        print("   ✅ Admin Panel معد بشكل صحيح")
    except Exception as e:
        print(f"   ❌ خطأ في Admin: {str(e)}")
        return
    
    print()
    
    # Test 4: Check URLs
    print("4. اختبار URLs...")
    try:
        from api.urls_notifications import urlpatterns
        print(f"   ✅ {len(urlpatterns)} URLs معدة")
    except Exception as e:
        print(f"   ❌ خطأ في URLs: {str(e)}")
        return
    
    print()
    
    # Test 5: Database Tables
    print("5. اختبار Database...")
    try:
        from api.models_notifications import FCMToken, Notification
        token_count = FCMToken.objects.count()
        notif_count = Notification.objects.count()
        print(f"   ✅ FCM Tokens: {token_count}")
        print(f"   ✅ Notifications: {notif_count}")
    except Exception as e:
        print(f"   ❌ خطأ في Database: {str(e)}")
        return
    
    print()
    print("=" * 60)
    print("  ✅ جميع الاختبارات نجحت!")
    print("=" * 60)
    print()
    print("النظام جاهز للاستخدام!")
    print()
    print("⏭️  الخطوة التالية:")
    print("   1. شغل التطبيق على جهاز حقيقي")
    print("   2. سجل دخول في التطبيق")
    print("   3. التطبيق سيرسل FCM Token تلقائياً")
    print("   4. ارجع لـ Admin Panel وأرسل إشعار")
    print()
    print("أو:")
    print("   - انتظر حتى نشر التطبيق")
    print("   - استخدم ngrok للاتصال بـ local backend")
    print()

if __name__ == '__main__':
    test_firebase_setup()
