#!/usr/bin/env python
"""
سكربت متقدم لاختبار وتشخيص مشكلة المراجعات
"""
import requests
import json
import sys
from datetime import datetime

# تكوين
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# ألوان للطباعة
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_colored(msg, color):
    print(f"{color}{msg}{Colors.END}")

def print_header(title):
    print("\n" + "="*60)
    print_colored(f"   {title}", Colors.BLUE)
    print("="*60)

def test_authentication():
    """اختبار المصادقة"""
    print_header("اختبار المصادقة")
    
    # خيارات المصادقة
    print("\nكيف تريد المصادقة؟")
    print("1. استخدام Token موجود")
    print("2. تسجيل الدخول باستخدام OTP")
    
    choice = input("\nاختر (1 أو 2): ")
    
    if choice == "1":
        token = input("أدخل Token: ")
        return token
    else:
        phone_number = input("أدخل رقم الهاتف: ")
        
        # طلب OTP
        print("\n📱 إرسال OTP...")
        otp_response = requests.post(f"{BASE_URL}/users/send-otp/", json={"phone_number": phone_number})
        
        if otp_response.status_code != 200:
            print_colored(f"✗ فشل إرسال OTP: {otp_response.text}", Colors.RED)
            return None
        
        print_colored("✓ تم إرسال OTP بنجاح", Colors.GREEN)
        
        # إدخال OTP
        otp = input("أدخل رمز OTP الذي وصلك: ")
        
        # التحقق من OTP
        print("\n🔐 التحقق من OTP...")
        verify_response = requests.post(f"{BASE_URL}/users/verify-otp/", json={
            "phone_number": phone_number,
            "otp": otp
        })
        
        if verify_response.status_code != 200:
            print_colored(f"✗ فشل التحقق من OTP: {verify_response.text}", Colors.RED)
            return None
        
        token = verify_response.json().get('token')
        print_colored(f"✓ تم التحقق بنجاح. Token: {token[:20]}...", Colors.GREEN)
        return token

def test_merchant_exists(merchant_id):
    """التحقق من وجود المتجر"""
    print_header(f"فحص المتجر #{merchant_id}")
    
    response = requests.get(f"{API_URL}/merchants/{merchant_id}/")
    
    if response.status_code == 200:
        data = response.json()
        print_colored(f"✓ المتجر موجود: {data.get('business_name', 'غير معروف')}", Colors.GREEN)
        print(f"  - التقييمات: {data.get('reviews_count', 0)}")
        print(f"  - المعدل: {data.get('average_rating', 0)}")
        return True
    else:
        print_colored(f"✗ المتجر غير موجود (Status: {response.status_code})", Colors.RED)
        return False

def test_review_creation(token, merchant_id):
    """اختبار إنشاء المراجعة"""
    print_header("اختبار إنشاء المراجعة")
    
    # اختبار مع Token format
    print("\n1️⃣ محاولة مع Token format...")
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    review_data = {
        "rating": 4,
        "comment": f"تقييم تجريبي - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    print(f"البيانات المرسلة: {json.dumps(review_data, ensure_ascii=False)}")
    
    response = requests.post(
        f"{API_URL}/merchants/{merchant_id}/reviews/create/",
        json=review_data,
        headers=headers
    )
    
    analyze_response(response, "Token")
    
    # إذا فشلت، جرب Bearer format
    if response.status_code != 201:
        print("\n2️⃣ محاولة مع Bearer format...")
        headers["Authorization"] = f"Bearer {token}"
        
        response = requests.post(
            f"{API_URL}/merchants/{merchant_id}/reviews/create/",
            json=review_data,
            headers=headers
        )
        
        analyze_response(response, "Bearer")
    
    return response.status_code == 201

def analyze_response(response, auth_type):
    """تحليل الاستجابة"""
    print(f"\n📊 تحليل الاستجابة ({auth_type}):")
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 201:
        print_colored("✓ تم إنشاء المراجعة بنجاح!", Colors.GREEN)
        data = response.json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif response.status_code == 400:
        print_colored("✗ خطأ في البيانات المرسلة", Colors.YELLOW)
        try:
            error = response.json()
            print(json.dumps(error, ensure_ascii=False, indent=2))
            
            # تحليل نوع الخطأ
            if 'error' in error:
                if 'مسبقاً' in error['error']:
                    print_colored("ℹ️ لقد قمت بتقييم هذا المتجر مسبقاً", Colors.YELLOW)
                else:
                    print_colored(f"ℹ️ {error['error']}", Colors.YELLOW)
        except:
            print(response.text)
    elif response.status_code == 401:
        print_colored("✗ مشكلة في المصادقة", Colors.RED)
        print(response.text)
    elif response.status_code == 404:
        print_colored("✗ المتجر غير موجود", Colors.RED)
    else:
        print_colored(f"✗ خطأ غير متوقع", Colors.RED)
        print(response.text)

def test_list_reviews(merchant_id):
    """عرض قائمة المراجعات"""
    print_header("قائمة المراجعات")
    
    response = requests.get(f"{API_URL}/merchants/{merchant_id}/reviews/")
    
    if response.status_code == 200:
        reviews = response.json()
        
        if isinstance(reviews, dict) and 'results' in reviews:
            reviews = reviews['results']
        
        if reviews:
            print_colored(f"✓ تم العثور على {len(reviews)} مراجعة", Colors.GREEN)
            for review in reviews[:3]:  # عرض أول 3 مراجعات فقط
                print(f"\n  📝 التقييم: {'⭐' * review.get('rating', 0)}")
                print(f"     التعليق: {review.get('comment', 'بدون تعليق')}")
                print(f"     التاريخ: {review.get('created_at', '')}")
                print(f"     المستخدم: {review.get('user_phone_number', 'غير معروف')}")
        else:
            print_colored("لا توجد مراجعات بعد", Colors.YELLOW)
    else:
        print_colored(f"✗ فشل جلب المراجعات: {response.status_code}", Colors.RED)

def main():
    print_colored("""
    ╔══════════════════════════════════════════╗
    ║   🔍 اختبار وتشخيص نظام المراجعات     ║
    ╚══════════════════════════════════════════╝
    """, Colors.BLUE)
    
    # 1. المصادقة
    token = test_authentication()
    if not token:
        print_colored("\n❌ فشلت المصادقة. إنهاء الاختبار.", Colors.RED)
        return
    
    print_colored(f"\n✓ Token: {token[:30]}...", Colors.GREEN)
    
    # 2. اختيار المتجر
    merchant_id = input("\n🏪 أدخل رقم المتجر للاختبار (افتراضي: 2): ") or "2"
    merchant_id = int(merchant_id)
    
    # 3. التحقق من وجود المتجر
    if not test_merchant_exists(merchant_id):
        print_colored("\n❌ المتجر غير موجود. إنهاء الاختبار.", Colors.RED)
        return
    
    # 4. اختبار إنشاء المراجعة
    test_review_creation(token, merchant_id)
    
    # 5. عرض المراجعات
    test_list_reviews(merchant_id)
    
    print_colored("""
    ╔══════════════════════════════════════════╗
    ║          ✅ انتهى الاختبار              ║
    ╚══════════════════════════════════════════╝
    """, Colors.GREEN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⚠️ تم إيقاف الاختبار من قبل المستخدم", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n\n❌ خطأ غير متوقع: {str(e)}", Colors.RED)
        import traceback
        traceback.print_exc()
