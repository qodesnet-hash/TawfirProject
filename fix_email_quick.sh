#!/bin/bash

echo "================================================"
echo "       🔧 حل سريع لمشكلة البريد الإلكتروني"
echo "================================================"
echo ""

echo "📝 هذا السكريبت يقوم بـ:"
echo "   1. حذف migration المشكل"
echo "   2. إعادة إنشاء migrations"
echo "   3. تطبيق التغييرات"
echo ""
echo "⚠️  تحذير: سيتم حذف migration القديم"
echo ""
read -p "اضغط Enter للمتابعة..."

echo ""
echo "⚙️  تفعيل البيئة الافتراضية..."
source venv/bin/activate

echo ""
echo "🔧 الخطوة 1: إصلاح البيانات المكررة في قاعدة البيانات..."
python fix_email_duplicates.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ فشل إصلاح البيانات!"
    echo "💡 جرب الحل اليدوي من خلال Django shell"
    read -p "اضغط Enter للخروج..."
    exit 1
fi

echo ""
echo "🗑️  الخطوة 2: حذف migration المشكل..."
rm users/migrations/0002_add_gmail_auth_fields.py

echo ""
echo "📝 الخطوة 3: تطبيق migrations المتبقية..."
python manage.py migrate users

echo ""
echo "🔄 الخطوة 4: إعادة إنشاء migrations..."
python manage.py makemigrations users

echo ""
echo "📊 الخطوة 5: تطبيق migrations الجديدة..."
python manage.py migrate users

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ فشل تطبيق migrations!"
    read -p "اضغط Enter للخروج..."
    exit 1
fi

echo ""
echo "================================================"
echo "          ✅ تم الإصلاح بنجاح!"
echo "================================================"
echo ""
read -p "اضغط Enter للخروج..."
