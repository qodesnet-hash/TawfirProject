# Generated migration for adding coordinates to City model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_offer_created_at_offer_views_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='خط العرض'),
        ),
        migrations.AddField(
            model_name='city',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='خط الطول'),
        ),
    ]
