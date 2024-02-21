# Generated by Django 3.2.23 on 2024-02-21 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0027_alter_lesson_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapterprogressstatus',
            name='progress',
            field=models.IntegerField(choices=[(0, 'Не начат'), (1, 'Начат'), (2, 'Пройден')], db_index=True, default=0, verbose_name='прогресс'),
        ),
        migrations.AlterField(
            model_name='course',
            name='status',
            field=models.IntegerField(choices=[(0, 'в разработке'), (1, 'опубликован'), (2, 'в архиве')], db_index=True, default=0, verbose_name='статус курса'),
        ),
        migrations.AlterField(
            model_name='courseprogressstatus',
            name='progress',
            field=models.IntegerField(choices=[(0, 'Не начат'), (1, 'Начат'), (2, 'Пройден')], db_index=True, default=0, verbose_name='прогресс'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='lesson_type',
            field=models.CharField(choices=[('Lesson', 'Урок'), ('Videolesson', 'Видеоурок'), ('Webinar', 'Вебинар'), ('Quiz', 'Тест'), ('Homework', 'Домашнее задание')], db_index=True, max_length=20, verbose_name='тип урока'),
        ),
        migrations.AlterField(
            model_name='lessonprogressstatus',
            name='progress',
            field=models.IntegerField(choices=[(0, 'Не начат'), (1, 'Начат'), (2, 'Пройден')], db_index=True, default=0, verbose_name='прогресс'),
        ),
    ]
