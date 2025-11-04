#!/usr/bin/env python
"""
حل SQL مباشر - تعديل حقل email في قاعدة البيانات
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from django.db import connection

def fix_email_column():
    """تعديل حقل email مباشرة في PostgreSQL"""
    
    print("="*60)
    print("🔧 إصلاح حقل email في قاعدة البيانات")
    print("="*60)
    
    with connection.cursor() as cursor:
        print("\n[1/4] إزالة قيد NOT NULL من email...")
        try:
            cursor.execute("""
                ALTER TABLE users_customuser 
                ALTER COLUMN email DROP NOT NULL;
            """)
            print("   ✓ تم إزالة NOT NULL")
        except Exception as e:
            print(f"   ℹ️  {e}")
        
        print("\n[2/4] تحويل القيم الفارغة إلى NULL...")
        cursor.execute("""
            UPDATE users_customuser 
            SET email = NULL 
            WHERE email = '';
        """)
        rows = cursor.rowcount
        print(f"   ✓ تم تحديث {rows} صف")
        
        print("\n[3/4] فحص القيم المكررة...")
        cursor.execute("""
            SELECT email, COUNT(*) 
            FROM users_customuser 
            WHERE email IS NOT NULL 
            GROUP BY email 
            HAVING COUNT(*) > 1;
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"   ⚠️  وجدنا {len(duplicates)} بريد مكرر")
            
            for email, count in duplicates:
                print(f"\n   🔧 إصلاح: {email} ({count} مرات)")
                
                # حذف email من الصفوف المكررة (نبقي على الأول)
                cursor.execute("""
                    WITH ranked AS (
                        SELECT id, 
                               ROW_NUMBER() OVER (
                                   PARTITION BY email 
                                   ORDER BY date_joined
                               ) as rn
                        FROM users_customuser 
                        WHERE email = %s
                    )
                    UPDATE users_customuser 
                    SET email = NULL 
                    WHERE id IN (
                        SELECT id FROM ranked WHERE rn > 1
                    );
                """, [email])
                print(f"      ✓ تم الإصلاح")
        else:
            print("   ✓ لا توجد قيم مكررة")
        
        print("\n[4/4] إزالة UNIQUE constraint القديم إن وُجد...")
        try:
            # البحث عن اسم constraint
            cursor.execute("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'users_customuser' 
                  AND constraint_type = 'UNIQUE' 
                  AND constraint_name LIKE '%email%';
            """)
            
            constraints = cursor.fetchall()
            for (constraint_name,) in constraints:
                print(f"   🗑️  حذف: {constraint_name}")
                cursor.execute(f"""
                    ALTER TABLE users_customuser 
                    DROP CONSTRAINT IF EXISTS {constraint_name};
                """)
            
            if not constraints:
                print("   ℹ️  لا توجد constraints قديمة")
            
        except Exception as e:
            print(f"   ℹ️  {e}")
    
    print("\n" + "="*60)
    print("✅ تم إصلاح حقل email بنجاح!")
    print("="*60)
    print("\n📝 الخطوة التالية:")
    print("   python manage.py migrate users")
    print("="*60)

if __name__ == '__main__':
    try:
        fix_email_column()
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
