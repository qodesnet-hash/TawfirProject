# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_fcmtoken_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchantrequest',
            name='merchant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.merchant', verbose_name='حساب التاجر'),
        ),
    ]
