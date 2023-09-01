# Generated by Django 3.2.20 on 2023-08-31 18:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Вопрос')),
                ('duration_minutes', models.PositiveIntegerField(default=0, verbose_name='Кол-во минут для сдачи')),
                ('passing_score', models.PositiveIntegerField(default=0, verbose_name='Кол-во баллов для прохождения')),
                ('retries', models.PositiveIntegerField(default=0, verbose_name='Число попыток')),
                ('slug', models.SlugField(unique=True)),
                ('status', models.CharField(max_length=20, verbose_name='Статус')),
                ('in_progress', models.BooleanField(default=False, verbose_name='В процессе')),
                ('deadline', models.DateTimeField(verbose_name='Срок выполнения')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Квиз',
                'verbose_name_plural': 'Квизы',
            },
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')),
                ('answers', models.JSONField(verbose_name='Ответы пользователя')),
                ('result', models.JSONField(verbose_name='Результат проверки ответов')),
                ('retry_count', models.PositiveIntegerField(default=0, verbose_name='Количество попыток')),
                ('score', models.PositiveIntegerField(default=0, verbose_name='Количество баллов')),
                ('final_result', models.CharField(max_length=255, verbose_name='Окончательный результат')),
                ('start_time', models.TimeField(blank=True, null=True, verbose_name='Время начала выполнения')),
                ('date_completed', models.TimeField(blank=True, null=True, verbose_name='Время завершения выполнения')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ответ пользователя',
                'verbose_name_plural': 'Ответы пользователей',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')),
                ('question_type', models.CharField(choices=[('checkbox', 'checkbox'), ('radio', 'radio'), ('text_answer', 'Text Answer')], max_length=20, verbose_name='Тип вопроса')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('answers', models.JSONField(verbose_name='[id, title, description, right_answer:bool]')),
                ('order_number', models.PositiveIntegerField(verbose_name='Порядковый номер')),
                ('quiz', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='quizzes.quiz', verbose_name='Квиз')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
                'ordering': ['order_number'],
            },
        ),
    ]