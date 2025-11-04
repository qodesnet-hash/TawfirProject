from django.urls import path
from .views_gmail_auth import (
    GoogleAuthView, 
    CompleteProfileView, 
    UpdateMerchantLocationView,
    check_profile_status,
    user_profile
)

urlpatterns = [
    # Gmail Auth routes (النظام الوحيد للمصادقة)
    path('api/google-auth/', GoogleAuthView.as_view(), name='google-auth'),
    path('api/complete-profile/', CompleteProfileView.as_view(), name='complete-profile'),
    path('api/merchant/update-location/', UpdateMerchantLocationView.as_view(), name='update-merchant-location'),
    path('api/check-profile/', check_profile_status, name='check-profile-status'),
    path('api/user-profile/', user_profile, name='user-profile'),
]
