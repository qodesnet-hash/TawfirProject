import requests
import json

# تكوين الاختبار
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# بيانات تسجيل الدخول للاختبار
login_data = {
    "phone_number": "01234567890",  # ضع رقم هاتف مستخدم حقيقي
    "password": "password123"  # وكلمة المرور الصحيحة
}

# تسجيل الدخول للحصول على التوكن
print("1. محاولة تسجيل الدخول...")
login_response = requests.post(f"{BASE_URL}/users/api/login/", json=login_data)

if login_response.status_code == 200:
    token = login_response.json().get('access')
    print(f"✓ تم تسجيل الدخول بنجاح. Token: {token[:20]}...")
    
    # إعداد الهيدرز
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # بيانات المراجعة
    review_data = {
        "rating": 5,
        "comment": "ممتاز جداً!"
    }
    
    # محاولة إضافة مراجعة
    merchant_id = 2  # ID المتجر
    print(f"\n2. محاولة إضافة مراجعة للمتجر رقم {merchant_id}...")
    print(f"   البيانات المرسلة: {json.dumps(review_data, ensure_ascii=False)}")
    
    review_response = requests.post(
        f"{API_URL}/merchants/{merchant_id}/reviews/create/",
        json=review_data,
        headers=headers
    )
    
    print(f"\n3. النتيجة:")
    print(f"   Status Code: {review_response.status_code}")
    print(f"   Response Headers: {dict(review_response.headers)}")
    print(f"   Response Body: {review_response.text}")
    
    if review_response.status_code == 201:
        print("✓ تم إنشاء المراجعة بنجاح!")
    elif review_response.status_code == 400:
        print("✗ خطأ في البيانات المرسلة")
        try:
            error_detail = review_response.json()
            print(f"   تفاصيل الخطأ: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
        except:
            print(f"   محتوى الخطأ: {review_response.text}")
    elif review_response.status_code == 401:
        print("✗ غير مصرح - تحقق من التوكن")
    elif review_response.status_code == 404:
        print("✗ المتجر غير موجود")
    else:
        print(f"✗ خطأ غير متوقع: {review_response.status_code}")

else:
    print(f"✗ فشل تسجيل الدخول: {login_response.status_code}")
    print(f"   Response: {login_response.text}")

print("\n" + "="*60)
print("اختبار إضافي: فحص المتجر")
print("="*60)

# فحص بيانات المتجر
merchant_response = requests.get(f"{API_URL}/merchants/{merchant_id}/")
if merchant_response.status_code == 200:
    merchant_data = merchant_response.json()
    print(f"المتجر: {merchant_data.get('business_name', 'غير معروف')}")
    print(f"التقييمات: {merchant_data.get('reviews_count', 0)}")
    print(f"المعدل: {merchant_data.get('average_rating', 0)}")
else:
    print(f"✗ لم أتمكن من جلب بيانات المتجر: {merchant_response.status_code}")
