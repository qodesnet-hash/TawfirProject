# Generated migration for Gmail auth support - Fixed duplicate email handling
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import users.managers

def fix_duplicate_emails(apps, schema_editor):
    """إصلاح القيم الفارغة والمكررة في حقل email قبل إضافة unique constraint"""
    db_alias = schema_editor.connection.alias
    CustomUser = apps.get_model('users', 'CustomUser')
    
    # 1. تحويل القيم الفارغة إلى NULL
    CustomUser.objects.using(db_alias).filter(email='').update(email=None)
    
    # 2. معالجة البريد الإلكتروني المكرر
    # الحصول على جميع الإيميلات المكررة
    from django.db.models import Count
    duplicates = (
        CustomUser.objects.using(db_alias)
        .values('email')
        .annotate(count=Count('email'))
        .filter(count__gt=1, email__isnull=False)
    )
    
    # لكل بريد مكرر، نبقي على أول مستخدم ونحذف email من الباقي
    for dup in duplicates:
        email = dup['email']
        users = CustomUser.objects.using(db_alias).filter(email=email).order_by('date_joined')
        
        # نبقي على أول مستخدم ونحذف email من الباقي
        for user in users[1:]:
            user.email = None
            user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('api', '0001_initial'),  # للـ City foreign key
    ]

    operations = [
        # تحديث المدير
        migrations.AlterModelManagers(
            name='customuser',
            managers=[
                ('objects', users.managers.CustomUserManager()),
            ],
        ),
        
        # إصلاح القيم المكررة BEFORE تطبيق unique constraint
        migrations.RunPython(
            fix_duplicate_emails,
            reverse_code=migrations.RunPython.noop
        ),
        
        # تعديل حقل email الموجود بدلاً من إضافته
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(
                blank=True, 
                null=True, 
                unique=True, 
                verbose_name='البريد الإلكتروني'
            ),
        ),
        
        # إضافة الحقول الجديدة
        migrations.AddField(
            model_name='customuser',
            name='full_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='الاسم الكامل'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(
                choices=[('customer', 'مستخدم عادي'), ('merchant', 'تاجر'), ('admin', 'مدير')], 
                default='customer', 
                max_length=20, 
                verbose_name='نوع المستخدم'
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='registration_method',
            field=models.CharField(
                choices=[('phone', 'رقم الهاتف'), ('google', 'Google'), ('email', 'البريد الإلكتروني')], 
                default='phone', 
                max_length=20, 
                verbose_name='طريقة التسجيل'
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='google_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='Google ID'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/', verbose_name='صورة الملف الشخصي'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True, verbose_name='تاريخ الميلاد'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='city',
            field=models.ForeignKey(
                blank=True, 
                null=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                related_name='users', 
                to='api.city', 
                verbose_name='المدينة'
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='العنوان التفصيلي'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_verified',
            field=models.BooleanField(
                default=False, 
                help_text='هل تم التحقق من البريد الإلكتروني أو رقم الهاتف', 
                verbose_name='تم التحقق'
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='merchant_verified',
            field=models.BooleanField(
                default=False, 
                help_text='هل تم التحقق من التاجر من قبل الإدارة', 
                verbose_name='تاجر موثق'
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='merchant_verified_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='تاريخ توثيق التاجر'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='preferences',
            field=models.JSONField(blank=True, default=dict, verbose_name='التفضيلات'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='notification_settings',
            field=models.JSONField(blank=True, default=dict, verbose_name='إعدادات الإشعارات'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='login_count',
            field=models.IntegerField(default=0, verbose_name='عدد مرات تسجيل الدخول'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_activity',
            field=models.DateTimeField(blank=True, null=True, verbose_name='آخر نشاط'),
        ),
        
        # إضافة حقل is_used لـ PhoneOTP
        migrations.AddField(
            model_name='phoneotp',
            name='is_used',
            field=models.BooleanField(default=False),
        ),
        
        # تعديل phone_number ليسمح بـ null
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(
                max_length=20,
                unique=True,
                null=True,
                blank=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message='رقم الجوال يجب أن يبدأ بـ 05 ويحتوي على 10 أرقام',
                        regex='^(05|5)\\d{8}$'
                    )
                ],
                verbose_name='رقم الجوال'
            ),
        ),
    ]
