#!/usr/bin/env python3
"""
Generate secure SECRET_KEY for Django
توليد SECRET_KEY آمن لـ Django
"""

import secrets
import string

def generate_secret_key(length=50):
    """
    توليد SECRET_KEY عشوائي وآمن
    Generate random and secure SECRET_KEY
    """
    # استخدام جميع الأحرف الآمنة
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    
    # توليد مفتاح عشوائي آمن
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return secret_key

def generate_db_password(length=24):
    """
    توليد كلمة مرور قوية لقاعدة البيانات
    Generate strong database password
    """
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*()_+-='
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

if __name__ == '__main__':
    print("="*70)
    print("🔐 Secure Credentials Generator - مولد البيانات الآمنة")
    print("="*70)
    print()
    
    print("📝 Django SECRET_KEY:")
    print("-" * 70)
    secret_key = generate_secret_key(50)
    print(secret_key)
    print()
    
    print("🔒 Database Password:")
    print("-" * 70)
    db_password = generate_db_password(24)
    print(db_password)
    print()
    
    print("="*70)
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("="*70)
    print("1. Copy these values to your .env file immediately")
    print("2. NEVER commit .env file to git")
    print("3. Keep these values secret and secure")
    print("4. Rotate credentials regularly (every 90 days)")
    print("5. Use different values for dev/staging/production")
    print()
    print("💡 To update .env file:")
    print("   1. Open .env file")
    print("   2. Update SECRET_KEY=<paste the key above>")
    print("   3. Update DB_PASSWORD=<paste the password above>")
    print("   4. Save and restart Django")
    print()
    print("="*70)
    
    # إنشاء ملف .env تلقائياً إذا لم يكن موجوداً
    try:
        with open('.env', 'r') as f:
            env_exists = True
    except FileNotFoundError:
        env_exists = False
    
    if not env_exists:
        print()
        print("⚠️  .env file not found!")
        create = input("Do you want to create .env file now? (y/n): ").lower()
        
        if create == 'y':
            with open('.env', 'w') as f:
                f.write(f"""# Django Settings
SECRET_KEY={secret_key}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=tawfir_db
DB_USER=postgres
DB_PASSWORD={db_password}
DB_HOST=localhost
DB_PORT=5432

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:8100,capacitor://localhost
CSRF_TRUSTED_ORIGINS=http://localhost:8100

# Media Files
MEDIA_ROOT=media
""")
            print("✅ .env file created successfully!")
            print("⚠️  Don't forget to update Twilio and Google credentials!")
    else:
        print()
        print("ℹ️  .env file already exists.")
        print("   Please update it manually with the credentials above.")
    
    print()
    print("="*70)
