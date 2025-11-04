import requests
import json

# تكوين الاختبار
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# بيانات المصادقة
phone_number = "01234567890"  # ضع رقم هاتف مستخدم حقيقي

# احصل على OTP أولاً (لأغراض التطوير فقط)
print("1. طلب OTP...")
otp_response = requests.post(f"{BASE_URL}/users/send-otp/", json={"phone_number": phone_number})
if otp_response.status_code == 200:
    print("✓ تم إرسال OTP")
    
    # في بيئة التطوير، قد تحتاج للحصول على OTP من قاعدة البيانات أو السجلات
    # للاختبار، أدخل OTP يدوياً
    otp = input("أدخل رمز OTP الذي وصلك: ")
    
    # التحقق من OTP
    print("2. التحقق من OTP...")
    verify_response = requests.post(f"{BASE_URL}/users/verify-otp/", json={
        "phone_number": phone_number,
        "otp": otp
    })
    
    if verify_response.status_code == 200:
        data = verify_response.json()
        token = data.get('token')
        print(f"✓ تم التحقق بنجاح. Token: {token[:20]}...")
        
        # إعداد الهيدرز - استخدام Token بدلاً من Bearer
        headers = {
            "Authorization": f"Token {token}",  # Token وليس Bearer
            "Content-Type": "application/json"
        }
        
        # بيانات المراجعة  
        review_data = {
            "rating": 5,
            "comment": "ممتاز جداً!"
        }
        
        # محاولة إضافة مراجعة
        merchant_id = 2  # ID المتجر
        print(f"\n3. محاولة إضافة مراجعة للمتجر رقم {merchant_id}...")
        print(f"   البيانات المرسلة: {json.dumps(review_data, ensure_ascii=False)}")
        
        review_response = requests.post(
            f"{API_URL}/merchants/{merchant_id}/reviews/create/",
            json=review_data,
            headers=headers
        )
        
        print(f"\n4. النتيجة:")
        print(f"   Status Code: {review_response.status_code}")
        
        if review_response.status_code == 201:
            print("✓ تم إنشاء المراجعة بنجاح!")
            print(f"   البيانات: {json.dumps(review_response.json(), ensure_ascii=False, indent=2)}")
        elif review_response.status_code == 400:
            print("✗ خطأ في البيانات المرسلة")
            try:
                error_detail = review_response.json()
                print(f"   تفاصيل الخطأ: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
            except:
                print(f"   محتوى الخطأ: {review_response.text}")
        elif review_response.status_code == 401:
            print("✗ غير مصرح - تحقق من التوكن")
            print(f"   الهيدرز المستخدمة: {headers}")
        elif review_response.status_code == 404:
            print("✗ المتجر غير موجود")
        else:
            print(f"✗ خطأ غير متوقع: {review_response.status_code}")
            print(f"   Response: {review_response.text}")
    else:
        print(f"✗ فشل التحقق من OTP: {verify_response.status_code}")
        print(f"   Response: {verify_response.text}")
else:
    print(f"✗ فشل إرسال OTP: {otp_response.status_code}")
    print(f"   Response: {otp_response.text}")

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
