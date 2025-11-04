#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings')
django.setup()

from django.db import connection

print("إصلاح حقل email...")

with connection.cursor() as cursor:
    # 1. إزالة NOT NULL
    cursor.execute("ALTER TABLE users_customuser ALTER COLUMN email DROP NOT NULL;")
    print("✓ إزالة NOT NULL")
    
    # 2. تحويل الفارغة لـ NULL
    cursor.execute("UPDATE users_customuser SET email = NULL WHERE email = '';")
    print(f"✓ تم تحديث {cursor.rowcount} صف")
    
    # 3. حل المكررات
    cursor.execute("""
        WITH ranked AS (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY email ORDER BY date_joined) as rn
            FROM users_customuser WHERE email IS NOT NULL
        )
        UPDATE users_customuser SET email = NULL 
        WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
    """)
    print(f"✓ حل {cursor.rowcount} تكرار")

print("\nالآن شغّل: python manage.py migrate users")
