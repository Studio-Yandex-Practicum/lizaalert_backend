# Generated by Django 3.2.20 on 2023-09-17 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_auto_20230917_2138'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('user',), 'verbose_name': ('Подписка на курс',)},
        ),
    ]
