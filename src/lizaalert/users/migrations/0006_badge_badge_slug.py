# Generated by Django 3.2.20 on 2024-02-02 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20240115_2001'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='badge_slug',
            field=models.SlugField(null=True, blank=True, max_length=100, unique=True, verbose_name='Поле поиска'),
        ),
    ]
