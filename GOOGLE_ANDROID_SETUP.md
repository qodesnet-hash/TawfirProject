# 🔐 إعداد Google Sign-In للتطبيق الأندرويد

## المشكلة
التطبيق على الهاتف يظهر: "تسجيل الدخول بـ Google غير متاح في بيئة التطوير"

## السبب
Google Console لديك OAuth Client لـ Web فقط، لكن التطبيق Native يحتاج Android OAuth Client

---

## 🚀 الحل: إنشاء Android OAuth Client

### الخطوة 1: احصل على SHA-1 Fingerprint

```bash
cd C:\Users\mus_2\GitHub\TawfirProject\frontend\tawfir_app\android

# للـ Debug
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android
```

أو على Windows:
```cmd
keytool -list -v -keystore "%USERPROFILE%\.android\debug.keystore" -alias androiddebugkey -storepass android -keypass android
```

ابحث عن السطر:
```
SHA1: XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX
```
**انسخ هذا الكود!**

---

### الخطوة 2: إضافة Android OAuth Client

1. افتح [Google Console](https://console.cloud.google.com/apis/credentials?project=tawfirapp-473717)

2. اضغط **+ CREATE CREDENTIALS** → **OAuth client ID**

3. اختر: **Android**

4. املأ البيانات:
   - **Name**: Tawfir Android App
   - **Package name**: انسخ من `android/app/build.gradle` (مثل: `com.tawfir.app`)
   - **SHA-1**: الصق الكود من الخطوة السابقة

5. اضغط **Create**

6. ✅ تم! لا تحتاج تحميل ملف JSON

---

### الخطوة 3: احصل على Package Name

```bash
cd android/app
```

افتح `build.gradle` وابحث عن:
```gradle
namespace "com.example.tawfir"  // هذا هو Package Name
```

---

### الخطوة 4: أعد Build التطبيق

```bash
cd C:\Users\mus_2\GitHub\TawfirProject\frontend\tawfir_app

ionic build
npx cap sync android
npx cap open android
```

ثم Run على الهاتف - **سيعمل Google Sign-In!** 🎉

---

## 📋 معلومات سريعة

### Client IDs المطلوبة:
1. ✅ **Web Client** (موجود): للـ ionic serve
2. ❌ **Android Client** (مطلوب): للهاتف

### بعد الإضافة:
- انتظر 5-10 دقائق لتفعيل Google
- لا تحتاج تعديل الكود
- سيعمل تلقائياً!

---

## 🔧 Troubleshooting

### إذا لم يعمل بعد:
1. تأكد من Package Name صحيح
2. تأكد من SHA-1 صحيح
3. انتظر 10 دقائق
4. أعد build التطبيق
5. جرّب مرة أخرى

### للحصول على SHA-1 بسرعة:
```cmd
cd android
gradlew signingReport
```
ابحث عن `SHA1` في النتائج
