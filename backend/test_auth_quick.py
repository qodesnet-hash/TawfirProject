#!/usr/bin/env python
"""
سكربت سريع لاختبار المصادقة
"""
import requests

BASE_URL = "http://localhost:8000"

def test_auth_with_token(token):
    """اختبار المصادقة باستخدام توكن"""
    
    print("\n" + "="*50)
    print("🔑 اختبار المصادقة")
    print("="*50)
    
    # اختبار 1: Token format
    print("\n1️⃣ محاولة مع Token format:")
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/check-auth/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ نجح! Response: {response.json()}")
    else:
        print(f"   ❌ فشل! Response: {response.text}")
    
    # اختبار 2: Bearer format
    print("\n2️⃣ محاولة مع Bearer format:")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/check-auth/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ نجح! Response: {response.json()}")
    else:
        print(f"   ❌ فشل! Response: {response.text}")
    
    # اختبار 3: بدون Authorization
    print("\n3️⃣ محاولة بدون Authorization:")
    response = requests.get(f"{BASE_URL}/api/v1/check-auth/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print(f"   ✅ صحيح - رفض الوصول بدون مصادقة")
    else:
        print(f"   ⚠️ غير متوقع! Status: {response.status_code}")

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║       🔐 اختبار نظام المصادقة           ║
    ╚══════════════════════════════════════════╝
    """)
    
    token = input("\n🎫 أدخل Token للاختبار: ").strip()
    
    if token:
        test_auth_with_token(token)
    else:
        print("❌ يجب إدخال Token!")
    
    print("\n✅ انتهى الاختبار\n")
