from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views_gmail_auth import (
    GoogleAuthView,
    CompleteProfileView,
    UpdateMerchantLocationView,
    check_profile_status,
    user_profile,
    upload_profile_picture,
    logout_view,
)

urlpatterns = [
    # Gmail Auth routes (النظام الوحيد للمصادقة)
    path('google-auth/', GoogleAuthView.as_view(), name='google-auth'),
    path('complete-profile/', CompleteProfileView.as_view(), name='complete-profile'),
    path('merchant/update-location/', UpdateMerchantLocationView.as_view(), name='update-merchant-location'),
    path('check-profile/', check_profile_status, name='check-profile-status'),
    path('user-profile/', user_profile, name='user-profile'),
    path('upload-profile-picture/', upload_profile_picture, name='upload-profile-picture'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),
]
