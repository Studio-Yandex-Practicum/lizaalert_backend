# Generated by Django 3.2.15 on 2023-02-28 18:27

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=120, null=True, verbose_name='название главы')),
            ],
            options={
                'verbose_name': 'глава',
                'verbose_name_plural': 'глава',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='ChapterLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='порядковый номер урока в главе')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата добавления урока в главу')),
            ],
            options={
                'verbose_name': 'Урок',
                'verbose_name_plural': 'Урок',
                'ordering': ('chapter', 'order_number'),
            },
        ),
        migrations.CreateModel(
            name='ChapterProgressStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('userchapterprogress', models.CharField(choices=[('0', 'Не начат'), ('1', 'Начат'), ('2', 'Пройден')], max_length=20, verbose_name='прогресс главы')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=120, verbose_name='Название курса')),
                ('format', models.CharField(max_length=60, verbose_name='Формат курса')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Дата начала курса')),
                ('cover_path', models.FileField(blank=True, null=True, upload_to='', verbose_name='Путь к обложке курса')),
                ('short_description', models.CharField(max_length=120, verbose_name='Краткое описание курса')),
                ('full_description', models.TextField(verbose_name='Полное описание курса')),
                ('knowledge', models.JSONField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Курс',
                'verbose_name_plural': 'Курсы',
            },
        ),
        migrations.CreateModel(
            name='CourseProgressStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('usercourseprogress', models.CharField(choices=[('0', 'Не начат'), ('1', 'Начат'), ('2', 'Пройден')], max_length=20, verbose_name='прогресс курса')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(editable=False, max_length=50, verbose_name='Статус курса')),
                ('slug', models.CharField(choices=[('active', 'Active'), ('complete', 'Complete'), ('registration', 'Registration')], default='active', editable=False, max_length=20)),
            ],
            options={
                'verbose_name': 'Статус курса',
                'verbose_name_plural': 'Статус курсов',
                'db_table': 'course_status',
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=120, verbose_name='название урока')),
                ('description', models.TextField(blank=True, null=True, verbose_name='описание урока')),
                ('lesson_type', models.CharField(choices=[('Lesson', 'Урок'), ('Videolesson', 'Видеоурок'), ('Webinar', 'Вебинар'), ('Quiz', 'Тест')], max_length=20, verbose_name='тип урока')),
                ('tags', models.CharField(max_length=255, verbose_name='ключевые слова урока')),
                ('duration', models.PositiveSmallIntegerField(verbose_name='продолжительность урока')),
                ('lesson_status', models.CharField(choices=[('Draft', 'В разработке'), ('Ready', 'Готов'), ('Published', 'Опубликован')], default='Draft', max_length=20, verbose_name='статус урока')),
                ('additional', models.BooleanField(default=False, verbose_name='дополнительный урок')),
                ('diploma', models.BooleanField(default=False, verbose_name='дипломный урок')),
            ],
            options={
                'verbose_name': 'Урок',
                'verbose_name_plural': 'Уроки',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='LessonProgressStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('userlessonprogress', models.CharField(choices=[('0', 'Не начат'), ('1', 'Начат'), ('2', 'Пройден')], max_length=20, verbose_name='прогресс урока')),
                ('version_number', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Номер версии урока')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lesson_progress', to='courses.lesson')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
