# Generated by Django 3.2.23 on 2024-02-11 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0021_Created_model_cohort'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cohort',
            options={'verbose_name': 'Когорта', 'verbose_name_plural': 'Когорты'},
        ),
        migrations.AddField(
            model_name='course',
            name='is_hidden',
            field=models.BooleanField(default=False, verbose_name='скрытый курс'),
        ),
    ]
