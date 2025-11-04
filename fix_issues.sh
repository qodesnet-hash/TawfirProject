#!/bin/bash
# Script لإصلاح المشاكل المتبقية في التطبيق

echo "📱 إصلاح مشاكل التطبيق..."

# 1. تثبيت Chart.js
echo "1️⃣ تثبيت Chart.js..."
cd C:\Users\mus_2\GitHub\TawfirProject\tawfir_app
npm install chart.js

# 2. إضافة URL للإعدادات في api/urls.py
echo "2️⃣ إضافة endpoint الإعدادات..."
# يجب إضافة هذا السطر في imports:
# from .merchant_views import MerchantSettingsUpdateView
# وإضافة هذا في urlpatterns:
# path('merchant/settings/update/', MerchantSettingsUpdateView.as_view(), name='merchant-settings-update'),

echo "✅ تم إنجاز الخطوات الأساسية"
echo ""
echo "📝 ملاحظات:"
echo "1. يجب إضافة endpoint الإعدادات في api/urls.py يدوياً"
echo "2. يجب إعادة تشغيل Backend: python manage.py runserver"
echo "3. يجب إعادة تشغيل Frontend: ionic serve"