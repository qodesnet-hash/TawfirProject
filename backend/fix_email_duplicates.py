#!/usr/bin/env python
"""
سكريبت لإصلاح مشكلة البريد الإلكتروني المكرر في قاعدة البيانات
يقوم بتحويل القيم الفارغة إلى NULL قبل إضافة قيد unique
"""
import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from django.db import connection

def fix_duplicate_emails():
    """إصلاح القيم الفارغة المكررة في حقل email"""
    
    print("🔧 بدء إصلاح مشكلة البريد الإلكتروني المكرر...")
    print("-" * 60)
    
    with connection.cursor() as cursor:
        # 1. فحص البيانات الحالية
        print("\n📊 فحص البيانات الحالية...")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(email) as users_with_email,
                COUNT(*) - COUNT(email) as users_without_email
            FROM users_customuser
        """)
        
        result = cursor.fetchone()
        total, with_email, without_email = result
        
        print(f"   ✓ إجمالي المستخدمين: {total}")
        print(f"   ✓ مستخدمين لديهم بريد إلكتروني: {with_email}")
        print(f"   ✓ مستخدمين بدون بريد إلكتروني: {without_email}")
        
        # 2. فحص القيم الفارغة
        print("\n🔍 فحص القيم الفارغة...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM users_customuser 
            WHERE email = '' OR email IS NULL
        """)
        empty_count = cursor.fetchone()[0]
        print(f"   ✓ عدد المستخدمين بقيمة email فارغة: {empty_count}")
        
        # 3. تحويل القيم الفارغة إلى NULL
        if empty_count > 0:
            print(f"\n🔄 تحويل {empty_count} قيمة فارغة إلى NULL...")
            cursor.execute("""
                UPDATE users_customuser 
                SET email = NULL 
                WHERE email = '' OR email IS NULL
            """)
            print(f"   ✓ تم التحديث بنجاح!")
        
        # 4. فحص القيم المكررة غير الفارغة
        print("\n🔍 فحص البريد الإلكتروني المكرر...")
        cursor.execute("""
            SELECT email, COUNT(*) as count
            FROM users_customuser 
            WHERE email IS NOT NULL AND email != ''
            GROUP BY email 
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"   ⚠️  تم العثور على {len(duplicates)} بريد إلكتروني مكرر:")
            for email, count in duplicates:
                print(f"      - {email}: {count} مرات")
                
                # حل المشكلة: الإبقاء على أول مستخدم وتعيين الباقي إلى NULL
                print(f"      🔧 إصلاح التكرارات...")
                cursor.execute("""
                    WITH ranked_users AS (
                        SELECT id, 
                               ROW_NUMBER() OVER (PARTITION BY email ORDER BY date_joined) as rn
                        FROM users_customuser 
                        WHERE email = %s
                    )
                    UPDATE users_customuser 
                    SET email = NULL 
                    WHERE id IN (
                        SELECT id FROM ranked_users WHERE rn > 1
                    )
                """, [email])
                print(f"      ✓ تم الإصلاح")
        else:
            print("   ✓ لا توجد قيم مكررة")
        
        # 5. التحقق النهائي
        print("\n✅ التحقق النهائي...")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT email) as unique_emails,
                COUNT(*) - COUNT(email) as null_emails
            FROM users_customuser
        """)
        
        total, unique, null = cursor.fetchone()
        print(f"   ✓ إجمالي المستخدمين: {total}")
        print(f"   ✓ بريد إلكتروني فريد: {unique}")
        print(f"   ✓ بريد إلكتروني NULL: {null}")
        
    print("\n" + "=" * 60)
    print("✅ تم إصلاح المشكلة بنجاح!")
    print("=" * 60)
    print("\n📝 الخطوة التالية:")
    print("   قم بتشغيل: python manage.py migrate users")
    print("-" * 60)

if __name__ == '__main__':
    try:
        fix_duplicate_emails()
    except Exception as e:
        print(f"\n❌ حدث خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
