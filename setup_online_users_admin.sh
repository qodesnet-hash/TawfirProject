#!/bin/bash

# إنشاء وتطبيق Migration لنموذج إعدادات المتواجدين

echo "====================================="
echo "إضافة نموذج إعدادات المتواجدين"
echo "====================================="

# 1. إضافة النموذج في models.py
echo "1. إضافة النموذج في api/models.py..."
cat api/models_online_users.py >> api/models.py

# 2. إضافة Admin في admin.py  
echo "2. إضافة Admin في api/admin.py..."
cat api/admin_online_users.py >> api/admin.py

# 3. إضافة Serializer في serializers.py
echo "3. إضافة Serializer في api/serializers.py..."
echo "" >> api/serializers.py
echo "# Online Users Settings Serializer" >> api/serializers.py
cat api/serializers_online_users.py >> api/serializers.py

# 4. إضافة Views في views.py
echo "4. إضافة Views في api/views.py..."
echo "" >> api/views.py
cat api/views_online_users.py >> api/views.py

# 5. إضافة URLs
echo "5. إضافة URL في api/urls.py..."
echo "" >> api/urls.py
echo "# Online Users Settings URL" >> api/urls.py
echo "from .views_online_users import OnlineUsersSettingsView" >> api/urls.py
echo "path('online-users-settings/', OnlineUsersSettingsView.as_view(), name='online-users-settings')," >> api/urls.py

# 6. إنشاء Migration
echo "6. إنشاء Migration..."
python manage.py makemigrations api

# 7. تطبيق Migration
echo "7. تطبيق Migration..."
python manage.py migrate

# 8. إنشاء إعدادات افتراضية
echo "8. إنشاء إعدادات افتراضية..."
python manage.py shell -c "
from api.models import OnlineUsersSettings
settings, created = OnlineUsersSettings.objects.get_or_create(
    pk=1,
    defaults={
        'enabled': True,
        'display_mode': 'full',
        'position': 'bottom',
        'min_users': 25,
        'max_users': 450,
        'peak_hours_start': 18,
        'peak_hours_end': 23
    }
)
if created:
    print('تم إنشاء إعدادات المتواجدين الافتراضية بنجاح')
else:
    print('الإعدادات موجودة مسبقاً')
"

echo "====================================="
echo "تمت إضافة الميزة بنجاح!"
echo "====================================="
echo ""
echo "يمكنك الآن:"
echo "1. الذهاب إلى لوحة تحكم Django Admin"
echo "2. البحث عن 'إعدادات المتواجدين'"
echo "3. تعديل الإعدادات حسب رغبتك"
echo ""
echo "API Endpoint: http://127.0.0.1:8000/api/v1/online-users-settings/"
