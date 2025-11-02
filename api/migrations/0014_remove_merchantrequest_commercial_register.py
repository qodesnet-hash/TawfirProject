# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_merchant_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='merchantrequest',
            name='commercial_register',
        ),
    ]
