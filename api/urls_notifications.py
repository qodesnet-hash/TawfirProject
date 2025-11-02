# api/urls_notifications.py
from django.urls import path
from .views_notifications import (
    save_fcm_token,
    delete_fcm_token,
    send_notification_admin,
    notifications_history
)

urlpatterns = [
    # للمستخدمين - حفظ/حذف Token
    path('fcm-token/', save_fcm_token, name='save_fcm_token'),
    path('fcm-token/delete/', delete_fcm_token, name='delete_fcm_token'),
    
    # للمدير فقط
    path('admin/send/', send_notification_admin, name='send_notification_admin'),
    path('admin/history/', notifications_history, name='notifications_history'),
]
