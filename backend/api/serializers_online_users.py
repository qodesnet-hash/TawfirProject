# إضافة في api/serializers.py

class OnlineUsersSettingsSerializer(serializers.ModelSerializer):
    """Serializer لإعدادات المتواجدين"""
    
    class Meta:
        model = OnlineUsersSettings
        fields = [
            'enabled',
            'display_mode',
            'position',
            'color_scheme',
            'custom_color',
            'opacity',
            'show_activity_status',
            'show_mini_chart',
            'show_pulse_animation',
            'auto_hide_on_scroll',
            'show_only_on_homepage',
            'update_interval',
            'min_users',
            'max_users',
            'peak_hours_start',
            'peak_hours_end',
            'sound_effects',
            'vibration_feedback',
        ]
