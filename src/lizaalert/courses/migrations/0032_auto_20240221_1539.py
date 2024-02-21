# Generated by Django 3.2.23 on 2024-02-21 12:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0031_auto_20240221_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='order_number',
            field=models.PositiveSmallIntegerField(blank=True, db_index=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='порядковый номер'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='order_number',
            field=models.PositiveSmallIntegerField(blank=True, db_index=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='порядковый номер'),
        ),
    ]
