# Generated manually for adding new position choices

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_onlineuserssettings'),  # الآن نشير للملف الصحيح
    ]

    operations = [
        migrations.AlterField(
            model_name='onlineuserssettings',
            name='position',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('bottom', 'وسط الأسفل'),
                    ('bottom-left', 'يسار الأسفل'),
                    ('bottom-right', 'يمين الأسفل'),
                    ('floating-center', 'عائم في الوسط'),
                    ('floating-left', 'عائم يسار'),
                    ('floating-right', 'عائم يمين'),
                ],
                default='bottom',
                verbose_name='موضع العداد'
            ),
        ),
    ]
