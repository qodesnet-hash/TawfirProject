"""
سكريبت للتحقق من بيانات المستخدم التاجر
"""
import os
import sys
import django

# إعداد Django
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Merchant

User = get_user_model()

print("=" * 60)
print("🔍 التحقق من بيانات المستخدم التاجر")
print("=" * 60)

# البحث عن جميع التجار
merchants = User.objects.filter(user_type='merchant')

if not merchants.exists():
    print("\n❌ لا يوجد أي مستخدم تاجر في قاعدة البيانات!")
    print("\nللتحويل إلى تاجر:")
    print("1. اذهب إلى Admin Panel")
    print("2. Users -> Custom Users")
    print("3. اختر المستخدم وغير user_type إلى 'merchant'")
else:
    print(f"\n✅ عدد التجار: {merchants.count()}\n")
    
    for user in merchants:
        print("-" * 60)
        print(f"📧 Email: {user.email}")
        print(f"📝 Full Name: {user.full_name}")
        print(f"👤 User Type: {user.user_type}")
        print(f"✅ Is Verified: {user.is_verified}")
        print(f"🛡️ Merchant Verified: {user.merchant_verified}")
        
        # التحقق من وجود Merchant profile
        try:
            merchant = Merchant.objects.get(user=user)
            print(f"🏪 Merchant Name: {merchant.business_name}")
            print(f"📍 Address: {merchant.address}")
            print(f"📊 Status: {merchant.status}")
        except Merchant.DoesNotExist:
            print("⚠️  تحذير: لا يوجد Merchant profile لهذا المستخدم!")
            print("   حل: أنشئ Merchant من Admin Panel")
        
        print("-" * 60)

print("\n" + "=" * 60)
print("✅ انتهى الفحص")
print("=" * 60)
