# Generated by Django 3.2.20 on 2023-10-30 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_auto_20231027_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='video_link',
            field=models.URLField(blank=True, null=True, verbose_name='Ссылка на видеоурок'),
        ),
    ]
