# Generated by Django 3.2.12 on 2022-06-02 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_level_name'),
        ('courses', '0003_coursestatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='level',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='course', to='users.level', verbose_name='Уровень'),
            preserve_default=False,
        ),
    ]
