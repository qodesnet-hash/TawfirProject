# api/urls_push_notifications.py
from django.urls import path
from .views_push_notifications import (
    NotificationPlanListView,
    MerchantNotificationCreditView,
    NotificationPurchaseRequestListView,
    NotificationPurchaseRequestCreateView,
    NotificationPurchaseUploadReceiptView,
    SendOfferNotificationView,
    MerchantNotificationHistoryView
)

urlpatterns = [
    # باقات الإشعارات
    path('notification-plans/', NotificationPlanListView.as_view(), name='notification-plans'),
    
    # رصيد التاجر
    path('notification-credit/', MerchantNotificationCreditView.as_view(), name='notification-credit'),
    
    # طلبات الشراء
    path('notification-purchases/', NotificationPurchaseRequestListView.as_view(), name='notification-purchases'),
    path('notification-purchases/create/', NotificationPurchaseRequestCreateView.as_view(), name='notification-purchase-create'),
    path('notification-purchases/<int:pk>/upload-receipt/', NotificationPurchaseUploadReceiptView.as_view(), name='notification-purchase-upload'),
    
    # إرسال الإشعارات
    path('send-notification/', SendOfferNotificationView.as_view(), name='send-notification'),
    
    # سجل الإشعارات
    path('notification-history/', MerchantNotificationHistoryView.as_view(), name='notification-history'),
]
