# Migration to remove OTP system - with proper email handling

from django.db import migrations, models
import uuid


def fix_null_emails(apps, schema_editor):
    """إصلاح المستخدمين الذين ليس لديهم email"""
    CustomUser = apps.get_model('users', 'CustomUser')
    
    # البحث عن المستخدمين بدون email
    users_without_email = CustomUser.objects.filter(email__isnull=True) | CustomUser.objects.filter(email='')
    
    count = users_without_email.count()
    if count > 0:
        print(f"\n⚠️  Found {count} users without email")
        print("Creating temporary emails for them...")
        
        for user in users_without_email:
            # إنشاء email مؤقت من رقم الهاتف أو UUID
            if user.phone_number:
                # استخدم رقم الهاتف
                temp_email = f"user_{user.phone_number}@temp.tawfir.app"
            else:
                # استخدم UUID عشوائي
                temp_email = f"user_{uuid.uuid4().hex[:8]}@temp.tawfir.app"
            
            user.email = temp_email
            user.save()
            print(f"  ✅ User {user.id}: {temp_email}")
        
        print(f"\n✅ Fixed {count} users")
        print("⚠️  NOTE: These users will need to register again with Gmail\n")


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_gmail_auth_fields'),
    ]

    operations = [
        # 1. إصلاح المستخدمين بدون email BEFORE جعل الحقل required
        migrations.RunPython(
            fix_null_emails,
            reverse_code=migrations.RunPython.noop
        ),
        
        # 2. الآن يمكننا جعل email NOT NULL
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(
                unique=True,
                verbose_name='البريد الإلكتروني'
            ),
        ),
        
        # 3. حذف جدول PhoneOTP
        migrations.DeleteModel(
            name='PhoneOTP',
        ),
        
        # 4. حذف حقل registration_method
        migrations.RemoveField(
            model_name='customuser',
            name='registration_method',
        ),
        
        # 5. تحديث phone_number ليكون اختياري تماماً
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(
                max_length=20,
                unique=True,
                null=True,
                blank=True,
                verbose_name='رقم الجوال'
            ),
        ),
    ]
