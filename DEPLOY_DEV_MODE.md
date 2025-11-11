# 🚀 دليل رفع تعديلات Dev Mode

## التعديلات المطلوبة

### ملف واحد فقط تغير:
- ✅ `backend/users/views_gmail_auth.py`

---

## 📤 خطوات الرفع

### 1. Push للـ GitHub

```bash
cd C:\Users\mus_2\GitHub\TawfirProject\backend

# تحقق من التغييرات
git status

# إضافة الملف
git add users/views_gmail_auth.py

# Commit
git commit -m "feat: Add dev_mode for localhost testing"

# Push
git push origin main
```

### 2. Deploy على DigitalOcean

```bash
# SSH للسيرفر
ssh root@your-server-ip

# انتقل لمجلد المشروع
cd /path/to/your/backend

# Pull التحديثات
git pull origin main

# Restart Gunicorn
sudo systemctl restart gunicorn

# تحقق من الحالة
sudo systemctl status gunicorn
```

---

## ✅ ملاحظات مهمة

### 🔒 الأمان:
- `dev_mode` يعمل **فقط** عندما `DEBUG=True`
- في Production (DigitalOcean) حيث `DEBUG=False`، سيتم تجاهل `dev_mode`
- لن يؤثر على الأمان في Production

### 🧪 الاختبار:
- **Localhost**: استخدم `dev_mode=true` للتجربة
- **Production**: Google Sign-In الحقيقي يعمل كالمعتاد

---

## ⚡ Quick Commands

### Windows (Git Bash):
```bash
cd backend
bash push_dev_mode.sh
```

### DigitalOcean:
```bash
ssh your-server
bash deploy_digitalocean.sh
```

---

## 🔍 التحقق من النجاح

بعد الـ Deploy، جرّب:

```bash
# على localhost
curl -X POST http://localhost:8000/auth/google-auth/ \
  -H "Content-Type: application/json" \
  -d '{"dev_mode": true, "email": "test@tawfir.app", "name": "Test User", "user_type": "customer", "id_token": "dev_token"}'

# يجب أن يعود بـ JWT tokens ✅
```

---

## ❓ المشاكل المحتملة

### مشكلة: Gunicorn لم يُعد التشغيل
```bash
sudo journalctl -u gunicorn -n 50
```

### مشكلة: الكود لم يتحدث
```bash
# تأكد من Pull
git log -1

# أعد تحميل الخدمة
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```
