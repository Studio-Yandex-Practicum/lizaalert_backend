# Generated by Django 3.2.20 on 2023-10-19 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_auto_20231016_1943'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapterprogressstatus',
            options={'ordering': ('user',), 'verbose_name': 'Прогресс по главе', 'verbose_name_plural': 'Прогресс по главам'},
        ),
        migrations.AlterModelOptions(
            name='courseprogressstatus',
            options={'ordering': ('user',), 'verbose_name': 'Прогресс по курсу', 'verbose_name_plural': 'Прогресс по курсам'},
        ),
        migrations.AlterModelOptions(
            name='lessonprogressstatus',
            options={'ordering': ('user',), 'verbose_name': 'Прогресс по уроку', 'verbose_name_plural': 'Прогресс по урокам'},
        ),
        migrations.AlterField(
            model_name='chapterprogressstatus',
            name='userchapterprogress',
            field=models.CharField(choices=[('0', 'Не начата'), ('1', 'Начата'), ('2', 'Пройдена')], max_length=20, verbose_name='прогресс главы'),
        ),
    ]
