#!/usr/bin/env python
"""
سكربت اختبار شامل لنظام المراجعات
يتعامل مع جميع السيناريوهات بما في ذلك المراجعات المكررة
"""
import requests
import json
from datetime import datetime

# تكوين
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_colored(msg, color):
    print(f"{color}{msg}{Colors.END}")

def print_header(title):
    print("\n" + "="*60)
    print_colored(f"   {title}", Colors.BLUE)
    print("="*60)

def get_auth_token():
    """الحصول على token للمصادقة"""
    print_header("المصادقة")
    
    print("\n1. استخدام Token موجود")
    print("2. الحصول على Token جديد عبر OTP")
    choice = input("\nاختر (1 أو 2): ")
    
    if choice == "1":
        token = input("أدخل Token: ")
        return token
    else:
        phone = input("أدخل رقم الهاتف: ")
        
        # إرسال OTP
        print_colored("\n📱 إرسال OTP...", Colors.CYAN)
        response = requests.post(f"{BASE_URL}/users/send-otp/", json={"phone_number": phone})
        
        if response.status_code != 200:
            print_colored(f"❌ فشل إرسال OTP: {response.text}", Colors.RED)
            return None
        
        print_colored("✅ تم إرسال OTP", Colors.GREEN)
        otp = input("أدخل رمز OTP: ")
        
        # التحقق من OTP
        response = requests.post(f"{BASE_URL}/users/verify-otp/", json={
            "phone_number": phone,
            "otp": otp
        })
        
        if response.status_code == 200:
            token = response.json().get('token')
            print_colored(f"✅ تم الحصول على Token: {token[:20]}...", Colors.GREEN)
            return token
        else:
            print_colored(f"❌ فشل التحقق: {response.text}", Colors.RED)
            return None

def check_existing_review(token, merchant_id):
    """التحقق من وجود مراجعة سابقة"""
    headers = {"Authorization": f"Token {token}"}
    
    # محاولة إضافة مراجعة وهمية للتحقق
    test_data = {"rating": 1, "comment": "test"}
    response = requests.post(
        f"{API_URL}/merchants/{merchant_id}/reviews/create/",
        json=test_data,
        headers=headers
    )
    
    if response.status_code == 400:
        data = response.json()
        if 'existing_review' in data:
            return data['existing_review']
    return None

def create_review(token, merchant_id, rating, comment):
    """إنشاء مراجعة جديدة"""
    print_header("إنشاء مراجعة جديدة")
    
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    data = {"rating": rating, "comment": comment}
    
    print(f"📝 البيانات المرسلة: {json.dumps(data, ensure_ascii=False)}")
    
    response = requests.post(
        f"{API_URL}/merchants/{merchant_id}/reviews/create/",
        json=data,
        headers=headers
    )
    
    print(f"\n📊 النتيجة:")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 201:
        print_colored("✅ تم إنشاء المراجعة بنجاح!", Colors.GREEN)
        review_data = response.json()
        print(f"   ID: {review_data.get('id')}")
        print(f"   التقييم: {'⭐' * review_data.get('rating', 0)}")
        print(f"   التعليق: {review_data.get('comment', 'بدون تعليق')}")
        return True, review_data
    
    elif response.status_code == 400:
        data = response.json()
        
        # التحقق من وجود مراجعة سابقة
        if 'existing_review' in data:
            print_colored("⚠️ لديك مراجعة سابقة لهذا المتجر!", Colors.YELLOW)
            existing = data['existing_review']
            print(f"\n📋 المراجعة الموجودة:")
            print(f"   ID: {existing.get('id')}")
            print(f"   التقييم: {'⭐' * existing.get('rating', 0)}")
            print(f"   التعليق: {existing.get('comment', 'بدون تعليق')}")
            print(f"   التاريخ: {existing.get('created_at')}")
            
            print_colored(f"\n💡 {data.get('suggestion', '')}", Colors.CYAN)
            return False, existing
        else:
            print_colored(f"❌ خطأ: {data.get('error', 'خطأ غير معروف')}", Colors.RED)
            if 'details' in data:
                print(f"   التفاصيل: {data['details']}")
            return False, None
    
    elif response.status_code == 401:
        print_colored("❌ مشكلة في المصادقة", Colors.RED)
        return False, None
    
    elif response.status_code == 404:
        print_colored("❌ المتجر غير موجود", Colors.RED)
        return False, None
    
    else:
        print_colored(f"❌ خطأ غير متوقع: {response.text}", Colors.RED)
        return False, None

def update_review(token, merchant_id, rating, comment):
    """تحديث مراجعة موجودة"""
    print_header("تحديث المراجعة")
    
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    data = {"rating": rating, "comment": comment}
    
    print(f"📝 البيانات الجديدة: {json.dumps(data, ensure_ascii=False)}")
    
    response = requests.put(
        f"{API_URL}/merchants/{merchant_id}/reviews/update/",
        json=data,
        headers=headers
    )
    
    if response.status_code == 200:
        print_colored("✅ تم تحديث المراجعة بنجاح!", Colors.GREEN)
        data = response.json()
        if 'review' in data:
            review = data['review']
            print(f"   التقييم الجديد: {'⭐' * review.get('rating', 0)}")
            print(f"   التعليق الجديد: {review.get('comment', 'بدون تعليق')}")
        return True
    else:
        print_colored(f"❌ فشل التحديث: {response.text}", Colors.RED)
        return False

def delete_review(token, merchant_id):
    """حذف مراجعة"""
    print_header("حذف المراجعة")
    
    confirm = input("هل أنت متأكد من حذف المراجعة؟ (yes/no): ")
    if confirm.lower() != 'yes':
        print("تم إلغاء الحذف")
        return False
    
    headers = {"Authorization": f"Token {token}"}
    
    response = requests.delete(
        f"{API_URL}/merchants/{merchant_id}/reviews/update/",
        headers=headers
    )
    
    if response.status_code == 200:
        print_colored("✅ تم حذف المراجعة بنجاح!", Colors.GREEN)
        return True
    else:
        print_colored(f"❌ فشل الحذف: {response.text}", Colors.RED)
        return False

def list_merchant_reviews(merchant_id):
    """عرض جميع مراجعات المتجر"""
    print_header(f"مراجعات المتجر #{merchant_id}")
    
    response = requests.get(f"{API_URL}/merchants/{merchant_id}/reviews/")
    
    if response.status_code == 200:
        data = response.json()
        
        # التعامل مع pagination
        reviews = data if isinstance(data, list) else data.get('results', [])
        
        if reviews:
            print_colored(f"✅ عدد المراجعات: {len(reviews)}", Colors.GREEN)
            for i, review in enumerate(reviews[:5], 1):  # أول 5 فقط
                print(f"\n  {i}. {'⭐' * review.get('rating', 0)}")
                print(f"     التعليق: {review.get('comment', 'بدون تعليق')}")
                print(f"     المستخدم: {review.get('user_phone_number', 'غير معروف')}")
                print(f"     التاريخ: {review.get('created_at', '')}")
        else:
            print_colored("لا توجد مراجعات بعد", Colors.YELLOW)
    else:
        print_colored(f"❌ فشل جلب المراجعات: {response.status_code}", Colors.RED)

def main():
    print_colored("""
    ╔═══════════════════════════════════════════╗
    ║     🌟 نظام اختبار المراجعات الشامل     ║
    ╚═══════════════════════════════════════════╝
    """, Colors.MAGENTA)
    
    # 1. المصادقة
    token = get_auth_token()
    if not token:
        print_colored("❌ فشلت المصادقة", Colors.RED)
        return
    
    # 2. اختيار المتجر
    merchant_id = input("\n🏪 أدخل رقم المتجر (افتراضي: 2): ") or "2"
    merchant_id = int(merchant_id)
    
    # 3. عرض القائمة
    while True:
        print_header("القائمة الرئيسية")
        print("1. إنشاء مراجعة جديدة")
        print("2. تحديث مراجعتي")
        print("3. حذف مراجعتي")
        print("4. عرض جميع المراجعات")
        print("5. التحقق من وجود مراجعة سابقة")
        print("6. تجربة سيناريو المراجعة المكررة")
        print("0. خروج")
        
        choice = input("\nاختر: ")
        
        if choice == "1":
            rating = int(input("التقييم (1-5): "))
            comment = input("التعليق (اختياري): ")
            success, data = create_review(token, merchant_id, rating, comment)
            
            if not success and data:
                # عرض خيار التحديث
                update_choice = input("\nهل تريد تحديث المراجعة الموجودة؟ (yes/no): ")
                if update_choice.lower() == 'yes':
                    new_rating = int(input("التقييم الجديد (1-5): "))
                    new_comment = input("التعليق الجديد: ")
                    update_review(token, merchant_id, new_rating, new_comment)
        
        elif choice == "2":
            rating = int(input("التقييم الجديد (1-5): "))
            comment = input("التعليق الجديد: ")
            update_review(token, merchant_id, rating, comment)
        
        elif choice == "3":
            delete_review(token, merchant_id)
        
        elif choice == "4":
            list_merchant_reviews(merchant_id)
        
        elif choice == "5":
            existing = check_existing_review(token, merchant_id)
            if existing:
                print_colored("✅ لديك مراجعة سابقة:", Colors.YELLOW)
                print(f"   التقييم: {'⭐' * existing.get('rating', 0)}")
                print(f"   التعليق: {existing.get('comment', 'بدون تعليق')}")
            else:
                print_colored("✅ لا توجد مراجعة سابقة", Colors.GREEN)
        
        elif choice == "6":
            print_header("اختبار المراجعة المكررة")
            print("سنحاول إضافة مراجعتين للتأكد من منع التكرار...")
            
            # المحاولة الأولى
            print_colored("\n1️⃣ المحاولة الأولى:", Colors.CYAN)
            success1, _ = create_review(token, merchant_id, 5, "المحاولة الأولى")
            
            # المحاولة الثانية
            print_colored("\n2️⃣ المحاولة الثانية (يجب أن تفشل):", Colors.CYAN)
            success2, existing = create_review(token, merchant_id, 4, "المحاولة الثانية")
            
            if success1 and not success2:
                print_colored("\n✅ النظام يعمل بشكل صحيح - منع التكرار!", Colors.GREEN)
            elif not success1 and not success2:
                print_colored("\n⚠️ لديك مراجعة سابقة بالفعل", Colors.YELLOW)
        
        elif choice == "0":
            print_colored("\n👋 مع السلامة!", Colors.CYAN)
            break
        
        else:
            print_colored("❌ خيار غير صحيح", Colors.RED)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⚠️ تم الإيقاف", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n❌ خطأ: {str(e)}", Colors.RED)
        import traceback
        traceback.print_exc()
