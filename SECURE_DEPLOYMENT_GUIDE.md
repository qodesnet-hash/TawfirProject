# 🔐 دليل النشر الآمن - Secure Deployment Guide

## تطبيق توفير - Tawfir App

---

## 📋 قائمة التحقق قبل النشر (Pre-Deployment Checklist)

### ✅ المرحلة 1: إعدادات الأمان الأساسية

- [ ] **تغيير SECRET_KEY**
  ```bash
  python generate_secure_credentials.py
  # انسخ المفتاح الجديد إلى .env
  ```

- [ ] **تعيين DEBUG=False**
  ```env
  DEBUG=False
  ```

- [ ] **تحديث ALLOWED_HOSTS**
  ```env
  ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
  ```

- [ ] **كلمة مرور قاعدة البيانات قوية**
  - 16+ حرف
  - أحرف كبيرة وصغيرة
  - أرقام ورموز
  ```bash
  python generate_secure_credentials.py
  ```

### ✅ المرحلة 2: بيانات الاعتماد

- [ ] **تدوير Twilio Credentials** (إذا تم كشفها)
  - اذهب إلى: https://console.twilio.com/
  - احصل على credentials جديدة
  - حدّث .env

- [ ] **التحقق من Google Client ID**
  - تأكد من تحديث Authorized origins
  - تأكد من تحديث Redirect URIs

- [ ] **تغيير URL الأدمن**
  ```env
  ADMIN_URL=your-secret-admin-path/
  ```

### ✅ المرحلة 3: HTTPS & SSL

- [ ] **الحصول على شهادة SSL**
  - استخدم Let's Encrypt (مجاني)
  - أو خدمة SSL مدفوعة

- [ ] **تفعيل HTTPS في Django**
  ```python
  # في settings_production.py
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  ```

- [ ] **إعداد Nginx/Apache للـ HTTPS**

### ✅ المرحلة 4: قاعدة البيانات

- [ ] **تأمين PostgreSQL**
  ```bash
  # تغيير كلمة مرور postgres
  sudo -u postgres psql
  \password postgres
  ```

- [ ] **تقييد الوصول**
  ```bash
  # تحرير pg_hba.conf
  # السماح فقط من localhost أو IPs محددة
  ```

- [ ] **إعداد Backups تلقائية**
  ```bash
  # Cron job للنسخ الاحتياطي اليومي
  0 2 * * * pg_dump tawfir_db > /backup/tawfir_$(date +\%Y\%m\%d).sql
  ```

### ✅ المرحلة 5: Middleware الأمني

- [ ] **تفعيل Security Middleware**
  ```python
  # في settings_production.py
  MIDDLEWARE = [
      'tawfir_backend.middleware.security.SecurityHeadersMiddleware',
      'tawfir_backend.middleware.security.RateLimitMiddleware',
      'tawfir_backend.middleware.security.AuditLoggingMiddleware',
      # ... باقي middleware
  ]
  ```

### ✅ المرحلة 6: Static & Media Files

- [ ] **جمع Static Files**
  ```bash
  python manage.py collectstatic --noinput
  ```

- [ ] **تأمين Media Files**
  ```bash
  # تعيين الصلاحيات المناسبة
  chmod 755 media/
  ```

- [ ] **(اختياري) نقل Media إلى S3**
  - أكثر أماناً وقابلية للتوسع

---

## 🚀 خطوات النشر (Deployment Steps)

### 1. تحديث الكود

```bash
# على الخادم
cd /path/to/TawfirProject
git pull origin main
```

### 2. تثبيت المتطلبات

```bash
# تفعيل البيئة الافتراضية
source venv/bin/activate

# تثبيت المكتبات الجديدة
pip install -r requirements_secure.txt
```

### 3. تطبيق Migrations

```bash
python manage.py migrate
```

### 4. جمع Static Files

```bash
python manage.py collectstatic --noinput
```

### 5. إعادة تشغيل الخدمات

```bash
# Gunicorn
sudo systemctl restart gunicorn

# Nginx
sudo systemctl restart nginx
```

---

## 🔍 الفحوصات بعد النشر (Post-Deployment Tests)

### اختبارات الأمان الأساسية

```bash
# 1. التحقق من HTTPS
curl -I https://yourdomain.com
# يجب أن ترى: Strict-Transport-Security

# 2. اختبار DEBUG=False
# افتح: https://yourdomain.com/nonexistent
# يجب أن ترى صفحة 404 بسيطة (ليس Django debug page)

# 3. اختبار ALLOWED_HOSTS
curl -H "Host: evil.com" https://yourdomain.com
# يجب أن يرجع: 400 Bad Request

# 4. اختبار Rate Limiting
# حاول تسجيل الدخول 15 مرة بكلمة مرور خاطئة
# يجب أن يتم حظرك مؤقتاً
```

### اختبارات API

```bash
# 1. اختبار Google Auth
curl -X POST https://yourdomain.com/api/v1/auth/api/google-auth/ \
  -H "Content-Type: application/json" \
  -d '{"id_token": "invalid_token"}'
# يجب أن يرجع: 401 Invalid token

# 2. اختبار JWT
curl https://yourdomain.com/api/v1/offers/ \
  -H "Authorization: Bearer invalid_token"
# يجب أن يرجع: 401 Unauthorized
```

---

## 📊 المراقبة والصيانة (Monitoring & Maintenance)

### 1. مراقبة Logs

```bash
# Django logs
tail -f logs/django.log

# Security logs
tail -f logs/security.log

# Nginx logs
tail -f /var/log/nginx/error.log
```

### 2. إعداد Monitoring

**باستخدام Sentry:**
```python
# في settings_production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
)
```

### 3. فحوصات أمنية دورية

```bash
# كل أسبوع: فحص الثغرات
python manage.py check --deploy

# كل شهر: تحديث المكتبات
pip list --outdated
pip install -U <package_name>

# كل 3 أشهر: تدوير Credentials
python generate_secure_credentials.py
```

---

## 🛡️ الحماية من الهجمات الشائعة

### 1. SQL Injection
✅ Django ORM يحمي تلقائياً
✅ لا تستخدم raw SQL أبداً
✅ SQLInjectionProtectionMiddleware نشط

### 2. XSS (Cross-Site Scripting)
✅ Django templates تهرب HTML تلقائياً
✅ X-XSS-Protection header مفعّل
✅ CSP headers مضافة

### 3. CSRF (Cross-Site Request Forgery)
✅ CSRF middleware مفعّل
✅ CSRF tokens مطلوبة
✅ SameSite cookies مفعّل

### 4. Brute Force
✅ Rate Limiting مفعّل (10 محاولات/دقيقة)
✅ Account lockout بعد 10 محاولات فاشلة
✅ Logging للمحاولات الفاشلة

### 5. DDoS
✅ Rate Limiting على API level
✅ استخدم Cloudflare للحماية الإضافية
✅ Nginx rate limiting

---

## 🔄 تدوير Credentials (Credential Rotation)

### كل 90 يوم:

1. **SECRET_KEY**
   ```bash
   python generate_secure_credentials.py
   # حدّث .env
   # أعد تشغيل Django
   ```

2. **Database Password**
   ```bash
   # في PostgreSQL
   ALTER USER postgres WITH PASSWORD 'new_password';
   # حدّث .env
   ```

3. **Twilio Credentials**
   - ادخل Twilio Console
   - احصل على credentials جديدة
   - حدّث .env

---

## 📞 الاتصال عند المشاكل

### Logs مهمة:
- `/logs/django.log` - أخطاء Django
- `/logs/security.log` - أحداث أمنية
- `/var/log/nginx/error.log` - أخطاء Nginx

### أدوات مساعدة:
```bash
# فحص حالة الخدمات
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql

# فحص المنافذ المفتوحة
sudo netstat -tulpn | grep LISTEN

# فحص استخدام الموارد
htop
df -h
```

---

## ⚠️ تحذيرات مهمة

1. **لا تنشر .env أبداً على git**
2. **غيّر جميع Credentials الافتراضية**
3. **فعّل Firewall على الخادم**
4. **قم بنسخ احتياطي يومي**
5. **راقب logs بانتظام**
6. **حدّث المكتبات شهرياً**
7. **استخدم HTTPS فقط في الإنتاج**
8. **لا تستخدم root user لتشغيل Django**

---

## ✅ قائمة التحقق النهائية

قبل إطلاق التطبيق للجمهور:

- [ ] جميع اختبارات الأمان نجحت
- [ ] HTTPS يعمل بشكل صحيح
- [ ] Backups تلقائية مفعّلة
- [ ] Monitoring & Logging يعمل
- [ ] جميع Credentials تم تغييرها
- [ ] Firewall مُعد بشكل صحيح
- [ ] Rate Limiting يعمل
- [ ] Error pages مخصصة
- [ ] سياسة الخصوصية منشورة
- [ ] شروط الاستخدام منشورة

---

**مبروك! التطبيق جاهز للنشر بشكل آمن! 🎉**
