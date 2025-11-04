#!/usr/bin/env python
"""
سكربت للتحقق من المراجعات المكررة وإدارتها
"""
import os
import django
import sys

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from api.models import Review, Merchant
from users.models import CustomUser
from django.db import connection

def check_duplicate_reviews():
    """فحص المراجعات المكررة"""
    print("\n" + "="*60)
    print("🔍 فحص المراجعات المكررة")
    print("="*60)
    
    # عرض جميع المراجعات
    reviews = Review.objects.all().select_related('user', 'merchant')
    
    if not reviews:
        print("❌ لا توجد أي مراجعات في قاعدة البيانات")
        return
    
    print(f"\n📊 إجمالي المراجعات: {reviews.count()}")
    print("\n📝 تفاصيل المراجعات:")
    print("-" * 60)
    
    for review in reviews[:10]:  # أول 10 مراجعات
        user_phone = getattr(review.user, 'phone_number', 'N/A')
        print(f"\n#{review.id}:")
        print(f"  👤 المستخدم: {user_phone}")
        print(f"  🏪 المتجر: {review.merchant.business_name} (ID: {review.merchant.id})")
        print(f"  ⭐ التقييم: {'⭐' * review.rating} ({review.rating}/5)")
        print(f"  💬 التعليق: {review.comment or 'بدون تعليق'}")
        print(f"  📅 التاريخ: {review.created_at}")

def check_user_reviews(phone_number):
    """فحص مراجعات مستخدم محدد"""
    try:
        user = CustomUser.objects.get(phone_number=phone_number)
        reviews = Review.objects.filter(user=user).select_related('merchant')
        
        print(f"\n👤 المستخدم: {phone_number}")
        print(f"📊 عدد المراجعات: {reviews.count()}")
        
        if reviews:
            print("\n📝 المتاجر التي تم تقييمها:")
            for review in reviews:
                print(f"  - {review.merchant.business_name} (ID: {review.merchant.id}) - {review.rating}⭐")
        else:
            print("✅ لم يقم هذا المستخدم بأي تقييمات بعد")
            
        return user, reviews
    except CustomUser.DoesNotExist:
        print(f"❌ لا يوجد مستخدم برقم: {phone_number}")
        return None, None

def check_merchant_reviews(merchant_id):
    """فحص مراجعات متجر محدد"""
    try:
        merchant = Merchant.objects.get(id=merchant_id)
        reviews = Review.objects.filter(merchant=merchant).select_related('user')
        
        print(f"\n🏪 المتجر: {merchant.business_name}")
        print(f"📊 عدد المراجعات: {reviews.count()}")
        
        if reviews:
            from django.db.models import Avg
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            print(f"⭐ متوسط التقييم: {avg_rating:.1f}")
            
            print("\n📝 المراجعات:")
            for review in reviews[:5]:  # أول 5 مراجعات
                user_phone = getattr(review.user, 'phone_number', 'N/A')
                print(f"  - {user_phone}: {review.rating}⭐ - {review.comment or 'بدون تعليق'}")
        else:
            print("✅ لا توجد مراجعات لهذا المتجر بعد")
            
        return merchant, reviews
    except Merchant.DoesNotExist:
        print(f"❌ لا يوجد متجر برقم: {merchant_id}")
        return None, None

def delete_review(user_phone, merchant_id):
    """حذف مراجعة محددة"""
    try:
        user = CustomUser.objects.get(phone_number=user_phone)
        merchant = Merchant.objects.get(id=merchant_id)
        review = Review.objects.get(user=user, merchant=merchant)
        
        print(f"\n🗑️ حذف المراجعة:")
        print(f"  المستخدم: {user_phone}")
        print(f"  المتجر: {merchant.business_name}")
        print(f"  التقييم: {review.rating}⭐")
        
        confirm = input("\nهل أنت متأكد؟ (yes/no): ")
        if confirm.lower() == 'yes':
            review.delete()
            print("✅ تم حذف المراجعة بنجاح")
            return True
        else:
            print("❌ تم إلغاء الحذف")
            return False
    except (CustomUser.DoesNotExist, Merchant.DoesNotExist, Review.DoesNotExist) as e:
        print(f"❌ خطأ: {str(e)}")
        return False

def main():
    print("""
    ╔═══════════════════════════════════════════╗
    ║     🔍 أداة فحص المراجعات المكررة        ║
    ╚═══════════════════════════════════════════╝
    """)
    
    while True:
        print("\n📋 الخيارات:")
        print("1. عرض جميع المراجعات")
        print("2. فحص مراجعات مستخدم محدد")
        print("3. فحص مراجعات متجر محدد")
        print("4. حذف مراجعة مكررة")
        print("5. فحص إذا كان مستخدم قام بتقييم متجر")
        print("0. خروج")
        
        choice = input("\nاختر رقم: ")
        
        if choice == "1":
            check_duplicate_reviews()
            
        elif choice == "2":
            phone = input("أدخل رقم الهاتف: ")
            check_user_reviews(phone)
            
        elif choice == "3":
            merchant_id = input("أدخل رقم المتجر: ")
            try:
                check_merchant_reviews(int(merchant_id))
            except ValueError:
                print("❌ رقم متجر غير صحيح")
                
        elif choice == "4":
            phone = input("أدخل رقم هاتف المستخدم: ")
            merchant_id = input("أدخل رقم المتجر: ")
            try:
                delete_review(phone, int(merchant_id))
            except ValueError:
                print("❌ رقم متجر غير صحيح")
                
        elif choice == "5":
            phone = input("أدخل رقم هاتف المستخدم: ")
            merchant_id = input("أدخل رقم المتجر: ")
            
            try:
                user = CustomUser.objects.get(phone_number=phone)
                merchant = Merchant.objects.get(id=int(merchant_id))
                
                existing = Review.objects.filter(user=user, merchant=merchant).first()
                
                if existing:
                    print(f"\n⚠️ نعم، المستخدم {phone} قام بتقييم {merchant.business_name} مسبقاً")
                    print(f"  التقييم: {existing.rating}⭐")
                    print(f"  التعليق: {existing.comment or 'بدون تعليق'}")
                    print(f"  التاريخ: {existing.created_at}")
                else:
                    print(f"\n✅ لا، المستخدم {phone} لم يقم بتقييم {merchant.business_name} بعد")
                    
            except CustomUser.DoesNotExist:
                print(f"❌ لا يوجد مستخدم برقم: {phone}")
            except Merchant.DoesNotExist:
                print(f"❌ لا يوجد متجر برقم: {merchant_id}")
            except ValueError:
                print("❌ رقم متجر غير صحيح")
                
        elif choice == "0":
            print("\n👋 مع السلامة!")
            break
        else:
            print("❌ خيار غير صحيح")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ تم الإيقاف")
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
