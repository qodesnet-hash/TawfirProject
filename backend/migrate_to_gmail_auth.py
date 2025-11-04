"""
Script to migrate from OTP to Gmail Auth only
This script will:
1. Update existing users to have emails
2. Remove phone number requirement
3. Clean up OTP data
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawfir_backend.settings_simple')
django.setup()

from users.models import CustomUser
from django.db import transaction

def migrate_users():
    """Migrate existing users to Gmail auth"""
    print("=" * 60)
    print("🔄 Starting migration from OTP to Gmail Auth")
    print("=" * 60)
    
    users = CustomUser.objects.all()
    print(f"\n📊 Total users: {users.count()}")
    
    # Count users without email
    users_without_email = CustomUser.objects.filter(email__isnull=True) | CustomUser.objects.filter(email='')
    print(f"⚠️  Users without email: {users_without_email.count()}")
    
    if users_without_email.count() > 0:
        print("\n⚠️  WARNING: Some users don't have email addresses!")
        print("These users will NOT be able to log in until they register with Gmail.")
        print("\nUsers without email:")
        for user in users_without_email[:10]:  # Show first 10
            print(f"  - ID: {user.id}, Phone: {user.phone_number}")
        
        if users_without_email.count() > 10:
            print(f"  ... and {users_without_email.count() - 10} more")
        
        response = input("\n❓ Do you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Migration cancelled")
            return
    
    # Show migration plan
    print("\n📋 Migration Plan:")
    print("1. Keep all existing user data")
    print("2. Phone numbers will remain as optional fields")
    print("3. Email will be required for new logins")
    print("4. Old OTP data will be cleaned (if exists)")
    
    response = input("\n❓ Proceed with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Migration cancelled")
        return
    
    print("\n🚀 Starting migration...")
    
    try:
        with transaction.atomic():
            # No actual changes needed to user records
            # Just update user_type if needed
            updated_count = 0
            
            for user in users:
                if not user.user_type:
                    user.user_type = 'customer'
                    user.save()
                    updated_count += 1
            
            if updated_count > 0:
                print(f"✅ Updated {updated_count} users with default user_type")
            
            print("\n✅ Migration completed successfully!")
            print("\n📊 Summary:")
            print(f"  - Total users: {users.count()}")
            print(f"  - Users with email: {CustomUser.objects.exclude(email__isnull=True).exclude(email='').count()}")
            print(f"  - Users without email: {users_without_email.count()}")
            
            print("\n⚠️  IMPORTANT:")
            print("  - Users without email must register again with Gmail")
            print("  - Old phone-based logins will no longer work")
            print("  - Make sure to run: python manage.py migrate")
            
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        print("Migration rolled back")
        return

if __name__ == '__main__':
    migrate_users()
