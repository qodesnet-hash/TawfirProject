#!/bin/bash

# ═══════════════════════════════════════════════════════════════════
# سكريبت إصلاح الأمان التلقائي - تطبيق توفير
# ═══════════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════════════"
echo "    🔒 سكريبت إصلاح الأمان - تطبيق توفير"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 غير مثبت!"
    exit 1
fi

echo "✅ Python موجود"
echo ""

# 1. النسخ الاحتياطي
echo "📦 جاري إنشاء نسخة احتياطية..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp .env "$BACKUP_DIR/" 2>/dev/null || echo "⚠️ .env not found"
cp tawfir_backend/settings.py "$BACKUP_DIR/" 2>/dev/null
cp tawfir_backend/settings_simple.py "$BACKUP_DIR/" 2>/dev/null
cp users/views_gmail_auth.py "$BACKUP_DIR/" 2>/dev/null
cp requirements.txt "$BACKUP_DIR/" 2>/dev/null
echo "✅ تم إنشاء نسخة احتياطية في: $BACKUP_DIR"
echo ""

# 2. تثبيت المكتبات الجديدة
echo "📥 جاري تثبيت المكتبات الأمنية..."
if [ -f "requirements_secure.txt" ]; then
    pip install -r requirements_secure.txt
    echo "✅ تم تثبيت المكتبات"
else
    echo "⚠️ requirements_secure.txt غير موجود"
fi
echo ""

# 3. نسخ الملفات الآمنة
echo "🔧 جاري تطبيق الإعدادات الآمنة..."

# نسخ settings الآمن
if [ -f "tawfir_backend/settings_secure.py" ]; then
    cp tawfir_backend/settings.py "tawfir_backend/settings_old_$(date +%Y%m%d).py"
    cp tawfir_backend/settings_secure.py tawfir_backend/settings.py
    echo "✅ تم تحديث settings.py"
else
    echo "⚠️ settings_secure.py غير موجود"
fi

# نسخ views الآمن
if [ -f "users/views_gmail_auth_secure.py" ]; then
    cp users/views_gmail_auth.py "users/views_gmail_auth_old_$(date +%Y%m%d).py"
    cp users/views_gmail_auth_secure.py users/views_gmail_auth.py
    echo "✅ تم تحديث views_gmail_auth.py"
else
    echo "⚠️ views_gmail_auth_secure.py غير موجود"
fi

# نسخ requirements الآمن
if [ -f "requirements_secure.txt" ]; then
    cp requirements.txt "requirements_old_$(date +%Y%m%d).txt"
    cp requirements_secure.txt requirements.txt
    echo "✅ تم تحديث requirements.txt"
fi

# نسخ .gitignore الآمن
if [ -f ".gitignore_secure" ]; then
    cp .gitignore ".gitignore_old_$(date +%Y%m%d)"
    cp .gitignore_secure .gitignore
    echo "✅ تم تحديث .gitignore"
fi

echo ""

# 4. توليد SECRET_KEY جديد
echo "🔑 جاري توليد SECRET_KEY جديد..."
NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
echo "✅ تم توليد SECRET_KEY جديد"
echo ""

# 5. إنشاء .env جديد
echo "📝 جاري إنشاء .env آمن..."
if [ ! -f ".env" ] || [ -f ".env.secure" ]; then
    cat > .env << EOF
# ══════════════════════════════════════════════════════════════════
# ⚠️ IMPORTANT: لا ترفع هذا الملف على Git!
# ══════════════════════════════════════════════════════════════════

SECRET_KEY=$NEW_SECRET
DEBUG=True
ENVIRONMENT=development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=tawfir_db
DB_USER=postgres
DB_PASSWORD=CHANGE_THIS_PASSWORD_NOW
DB_HOST=localhost
DB_PORT=5432

# Twilio - ⚠️ أعد إصدار credentials جديدة!
TWILIO_ACCOUNT_SID=YOUR_TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN=YOUR_TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER=YOUR_TWILIO_PHONE_NUMBER

# Google OAuth
GOOGLE_CLIENT_ID=409608657151-95dqok74ojre9b6u377f1vsritt6afb3.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:8100,capacitor://localhost,ionic://localhost

MEDIA_ROOT=media
ADMIN_EMAIL=admin@tawfir.app
EOF
    echo "✅ تم إنشاء .env جديد"
    echo "⚠️ تذكر: غيّر كلمة مرور قاعدة البيانات و Twilio credentials"
else
    echo "⚠️ .env موجود بالفعل، لم يتم استبداله"
fi
echo ""

# 6. إنشاء مجلد logs
echo "📁 جاري إنشاء مجلد logs..."
mkdir -p logs
touch logs/.gitkeep
echo "✅ تم إنشاء مجلد logs"
echo ""

# 7. تحديث manage.py
echo "🔧 جاري تحديث manage.py..."
if grep -q "settings_simple" manage.py; then
    sed -i "s/settings_simple/settings/g" manage.py
    echo "✅ تم تحديث manage.py"
fi
echo ""

# 8. عمل migrations
echo "🔄 جاري تطبيق migrations..."
python3 manage.py makemigrations
python3 manage.py migrate
echo "✅ تم تطبيق migrations"
echo ""

# 9. فحص النشر
echo "🔍 جاري فحص إعدادات النشر..."
python3 manage.py check --deploy || echo "⚠️ يوجد تحذيرات"
echo ""

# 10. التعليمات النهائية
echo "═══════════════════════════════════════════════════════════════════"
echo "    ✅ انتهى الإصلاح!"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "📋 الخطوات المطلوبة منك:"
echo ""
echo "1. ⚠️ غيّر كلمة مرور قاعدة البيانات في .env"
echo "2. ⚠️ أعد إصدار Twilio credentials وحدّث .env"
echo "3. ⚠️ احصل على Google Client Secret وحدّث .env"
echo "4. 🔒 احذف .env من تاريخ Git:"
echo "   git filter-branch --force --index-filter \\"
echo "   \"git rm --cached --ignore-unmatch .env\" \\"
echo "   --prune-empty --tag-name-filter cat -- --all"
echo ""
echo "5. 🚀 جرب التطبيق:"
echo "   python manage.py runserver"
echo ""
echo "6. 📚 اقرأ التقارير:"
echo "   - SECURITY_AUDIT_REPORT.txt"
echo "   - DEPLOYMENT_GUIDE_SECURE.txt"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "    النسخة الاحتياطية في: $BACKUP_DIR"
echo "═══════════════════════════════════════════════════════════════════"
