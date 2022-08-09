# Generated by Django 3.2.12 on 2022-07-31 23:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='user_created',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lesson_creator', to=settings.AUTH_USER_MODEL, verbose_name='пользователь, создавший урок'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='user_modifier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lesson_editor', to=settings.AUTH_USER_MODEL, verbose_name='пользователь, внёсший изменения в урок'),
        ),
        migrations.AddField(
            model_name='course',
            name='level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='course', to='users.level', verbose_name='Уровень'),
        ),
        migrations.AddField(
            model_name='course',
            name='user_created',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Создатель курса'),
        ),
        migrations.AddField(
            model_name='chapterlesson',
            name='chapter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='courses.chapter'),
        ),
        migrations.AddField(
            model_name='chapterlesson',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='courses.lesson'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chapters', to='courses.course', verbose_name='Части'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='lessons',
            field=models.ManyToManyField(through='courses.ChapterLesson', to='courses.Lesson', verbose_name='уроки главы'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='user_created',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chapter_creator', to=settings.AUTH_USER_MODEL, verbose_name='пользователь, создавший главу'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='user_modifier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chapter_editor', to=settings.AUTH_USER_MODEL, verbose_name='пользователь, внёсший изменения в главу'),
        ),
        migrations.AddConstraint(
            model_name='chapterlesson',
            constraint=models.UniqueConstraint(fields=('chapter', 'lesson', 'order_number'), name='unique_chapter_lesson'),
        ),
    ]
