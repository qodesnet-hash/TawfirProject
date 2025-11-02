# api/views_online_users.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import OnlineUsersSettings
from .serializers import OnlineUsersSettingsSerializer

class OnlineUsersSettingsView(APIView):
    """API لجلب إعدادات المتواجدين من لوحة التحكم"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        # جلب الإعدادات أو إنشاء افتراضية
        settings, created = OnlineUsersSettings.objects.get_or_create(
            pk=1,  # نريد سجل واحد فقط
            defaults={
                'enabled': True,
                'display_mode': 'full',
                'position': 'bottom',
                'color_scheme': 'dynamic',
                'opacity': 1.0,
                'show_activity_status': True,
                'show_mini_chart': True,
                'show_pulse_animation': True,
                'auto_hide_on_scroll': False,
                'show_only_on_homepage': False,
                'update_interval': 10,
                'min_users': 25,
                'max_users': 450,
                'peak_hours_start': 18,
                'peak_hours_end': 23,
                'sound_effects': False,
                'vibration_feedback': False,
            }
        )
        
        if created:
            print("تم إنشاء إعدادات المتواجدين الافتراضية")
        
        serializer = OnlineUsersSettingsSerializer(settings)
        return Response(serializer.data)
