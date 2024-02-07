# Generated by Django 3.2.23 on 2024-02-05 20:18

from django.db import migrations, models


def create_levels(apps, schema_editor):
    Level = apps.get_model('users', 'Level')

    class LevelName(models.TextChoices):
        beginner = "novice", "Новичок"
        middle = "experienced", "Бывалый"
        professional = "professional", "Профессионал"

    for name, _ in LevelName.choices:
        Level.objects.get_or_create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20240115_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='level',
            name='name',
            field=models.CharField(choices=[('novice', 'Новичок'), ('experienced', 'Бывалый'), ('professional', 'Профессионал')], max_length=20, unique=True, verbose_name='Наименование уровня'),
        ),
        migrations.RunPython(create_levels),
    ]