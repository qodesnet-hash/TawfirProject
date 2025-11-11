# 🚀 حل مشكلة Google Sign-In في بيئة التطوير

## المشكلة
Google Sign-In يرفض العمل على `http://localhost:8100` في بيئة التطوير

## الحل المطبق

### ✅ Frontend (auth-gmail.page.ts)
تم إضافة وضع تطوير يتخطى Google SDK:

```typescript
// في حالة localhost، يظهر نافذة تسجيل دخول تجريبي
if (window.location.hostname === 'localhost') {
  await this.devModeLogin();  // تسجيل دخول تجريبي
}
```

### ✅ Backend (views_gmail_auth.py)
تم إضافة دعم `dev_mode` في API:

```python
dev_mode = request.data.get('dev_mode', False)
if dev_mode and settings.DEBUG:
    # تخطي التحقق من Google Token
    email = request.data.get('email')
    google_id = f"dev_{email}_{timestamp}"
```

## كيف تستخدمه؟

### في التطوير (localhost):
1. اختر نوع الحساب (مستخدم أو تاجر)
2. اضغط "تسجيل الدخول بـ Google"
3. ستظهر نافذة تسجيل دخول تجريبي
4. أدخل بريد وهمي مثل `test@tawfir.app`
5. سجّل الدخول

### في Production:
- سيعمل Google Sign-In الحقيقي تلقائياً
- لن يعمل dev_mode (لأن DEBUG=False)

## للتجربة على الهاتف الحقيقي:

```bash
cd frontend/tawfir_app
build_android.bat
```

ثم افتح في Android Studio وجرّب على جهاز حقيقي - سيعمل Google Sign-In بشكل طبيعي!

## ملاحظة مهمة
⚠️ لا تنسى تشغيل Backend في DigitalOcean قبل التجربة!
