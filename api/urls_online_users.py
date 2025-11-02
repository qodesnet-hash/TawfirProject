# إضافة في tawfir_backend/urls.py أو api/urls.py

from api.views_online_users import OnlineUsersSettingsView

urlpatterns = [
    # ... URLs الموجودة
    
    # Online Users Settings
    path('api/v1/online-users-settings/', OnlineUsersSettingsView.as_view(), name='online-users-settings'),
]
