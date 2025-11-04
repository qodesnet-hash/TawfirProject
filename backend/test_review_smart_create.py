#!/usr/bin/env python
"""
اختبار ميزة الإنشاء/التحديث الذكي للتقييمات
يختبر أن endpoint create يمكنه التعامل مع كل من الإنشاء والتحديث
"""

import requests
import json
import time

# تكوين الاختبار
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# بيانات تسجيل الدخول للاختبار
login_data = {
    "phone_number": "01234567890",  # ضع رقم هاتف مستخدم حقيقي
    "password": "password123"  # وكلمة المرور الصحيحة
}

def test_smart_review_create():
    """اختبار الإنشاء/التحديث الذكي للتقييمات"""
    
    print("="*60)
    print("اختبار ميزة الإنشاء/التحديث الذكي للتقييمات")
    print("="*60)
    
    # 1. تسجيل الدخول
    print("\n1. تسجيل الدخول...")
    login_response = requests.post(f"{BASE_URL}/users/api/login/", json=login_data)
    
    if login_response.status_code != 200:
        print(f"✗ فشل تسجيل الدخول: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        return
    
    token = login_response.json().get('access')
    print(f"✓ تم تسجيل الدخول بنجاح. Token: {token[:20]}...")
    
    # إعداد الهيدرز
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    merchant_id = 2  # ID المتجر للاختبار
    
    # 2. محاولة إنشاء تقييم جديد
    print(f"\n2. محاولة إنشاء تقييم جديد للمتجر #{merchant_id}...")
    
    first_review_data = {
        "rating": 4,
        "comment": "خدمة جيدة"
    }
    
    print(f"   البيانات: {json.dumps(first_review_data, ensure_ascii=False)}")
    
    first_response = requests.post(
        f"{API_URL}/merchants/{merchant_id}/reviews/create/",
        json=first_review_data,
        headers=headers
    )
    
    print(f"\n   النتيجة:")
    print(f"   Status Code: {first_response.status_code}")
    
    if first_response.status_code in [200, 201]:
        response_data = first_response.json()
        action = response_data.get('action', 'unknown')
        
        if action == 'created':
            print(f"   ✓ تم إنشاء تقييم جديد!")
        elif action == 'updated':
            print(f"   ✓ تم تحديث التقييم الموجود!")
        else:
            print(f"   ✓ تمت العملية بنجاح")
        
        if 'review' in response_data:
            review = response_data['review']
            print(f"   التقييم: {review.get('rating')} نجوم")
            print(f"   التعليق: {review.get('comment', 'لا يوجد')}")
    else:
        print(f"   ✗ فشلت العملية")
        print(f"   Response: {json.dumps(first_response.json(), ensure_ascii=False, indent=2)}")
        return
    
    # انتظار قليلاً
    print("\n   ⏳ انتظار 2 ثانية...")
    time.sleep(2)
    
    # 3. محاولة "إنشاء" تقييم آخر (يجب أن يحدث تحديث)
    print(f"\n3. محاولة إنشاء تقييم آخر (يجب أن يحدث تحديث)...")
    
    second_review_data = {
        "rating": 5,
        "comment": "ممتاز! خدمة رائعة"
    }
    
    print(f"   البيانات الجديدة: {json.dumps(second_review_data, ensure_ascii=False)}")
    
    second_response = requests.post(
        f"{API_URL}/merchants/{merchant_id}/reviews/create/",  # نفس endpoint
        json=second_review_data,
        headers=headers
    )
    
    print(f"\n   النتيجة:")
    print(f"   Status Code: {second_response.status_code}")
    
    if second_response.status_code in [200, 201]:
        response_data = second_response.json()
        action = response_data.get('action', 'unknown')
        
        if action == 'updated':
            print(f"   ✓ ممتاز! تم تحديث التقييم بنجاح بدلاً من إنشاء مكرر!")
        elif action == 'created':
            print(f"   ⚠️ تم إنشاء تقييم جديد (غير متوقع)")
        
        if 'review' in response_data:
            review = response_data['review']
            print(f"   التقييم المحدث: {review.get('rating')} نجوم")
            print(f"   التعليق المحدث: {review.get('comment', 'لا يوجد')}")
    else:
        print(f"   ✗ فشلت العملية")
        print(f"   Response: {json.dumps(second_response.json(), ensure_ascii=False, indent=2)}")
    
    # 4. التحقق من التقييمات للمتجر
    print(f"\n4. التحقق من التقييمات للمتجر...")
    
    reviews_response = requests.get(f"{API_URL}/merchants/{merchant_id}/reviews/")
    
    if reviews_response.status_code == 200:
        reviews = reviews_response.json()
        
        # عد التقييمات من المستخدم الحالي
        user_phone = login_data['phone_number']
        user_reviews = [r for r in reviews if r.get('user_phone_number') == user_phone]
        
        print(f"   عدد التقييمات من المستخدم الحالي: {len(user_reviews)}")
        
        if len(user_reviews) == 1:
            print(f"   ✓ ممتاز! يوجد تقييم واحد فقط (لم يتم إنشاء مكرر)")
            review = user_reviews[0]
            print(f"   التقييم النهائي: {review.get('rating')} نجوم")
            print(f"   التعليق النهائي: {review.get('comment', 'لا يوجد')}")
        elif len(user_reviews) > 1:
            print(f"   ⚠️ تحذير: يوجد {len(user_reviews)} تقييمات من نفس المستخدم!")
        else:
            print(f"   ℹ️ لا توجد تقييمات من هذا المستخدم")
    else:
        print(f"   ✗ فشل جلب التقييمات: {reviews_response.status_code}")
    
    print("\n" + "="*60)
    print("انتهى الاختبار")
    print("="*60)

if __name__ == "__main__":
    test_smart_review_create()
