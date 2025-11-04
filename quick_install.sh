#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "   تثبيت سريع للإصلاحات الأمنية"
echo "   Quick Security Fixes Installation"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 1. تثبيت google-auth
echo "📦 Installing google-auth..."
pip install google-auth google-auth-oauthlib --break-system-packages

# 2. توليد credentials جديدة
echo ""
echo "🔐 Generating new secure credentials..."
python generate_secure_credentials.py

# 3. تطبيق migrations
echo ""
echo "📊 Applying database migrations..."
python manage.py migrate

# 4. جمع static files
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Installation complete!"
echo ""
echo "⚠️  NEXT STEPS:"
echo "1. Update .env with new credentials"
echo "2. Rotate Twilio credentials from console.twilio.com"
echo "3. Change database password"
echo "4. Update settings module to settings_production"
echo "5. Restart Django server"
echo ""
echo "📖 Read: SECURITY_FIXES_SUMMARY.md for details"
echo "═══════════════════════════════════════════════════════════"
