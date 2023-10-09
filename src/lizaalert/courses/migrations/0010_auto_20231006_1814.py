# Generated by Django 3.2.20 on 2023-10-09 08:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_auto_20230811_1615'),
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quizzes', '0002_auto_20230919_1110'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='student', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lessonprogressstatus',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lesson_progress', to='courses.lesson'),
        ),
        migrations.AddField(
            model_name='lessonprogressstatus',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_lesson_status', to=settings.AUTH_USER_MODEL, verbose_name='user_lesson_status'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='chapter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lessons', to='courses.chapter', verbose_name='уроки главы'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='quiz',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quizzes.quiz', verbose_name='квиз'),
        ),
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
            model_name='knowledge',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Создатель умения'),
        ),
        migrations.AddField(
            model_name='faq',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Создатель вопроса'),
        ),
        migrations.AddField(
            model_name='courseprogressstatus',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='course_progress', to='courses.course'),
        ),
        migrations.AddField(
            model_name='courseprogressstatus',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_course_status', to=settings.AUTH_USER_MODEL, verbose_name='course_status'),
        ),
        migrations.AddField(
            model_name='courseknowledge',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course'),
        ),
        migrations.AddField(
            model_name='courseknowledge',
            name='knowledge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.knowledge'),
        ),
        migrations.AddField(
            model_name='coursefaq',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.course'),
        ),
        migrations.AddField(
            model_name='coursefaq',
            name='faq',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.faq'),
        ),
        migrations.AddField(
            model_name='course',
            name='faq',
            field=models.ManyToManyField(null=True, through='courses.CourseFaq', to='courses.FAQ', verbose_name='Часто задаваемые вопросы'),
        ),
        migrations.AddField(
            model_name='course',
            name='knowledge',
            field=models.ManyToManyField(null=True, through='courses.CourseKnowledge', to='courses.Knowledge', verbose_name='Умения'),
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
            model_name='chapterprogressstatus',
            name='chapter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chapter_progress', to='courses.chapter'),
        ),
        migrations.AddField(
            model_name='chapterprogressstatus',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_chapter_status', to=settings.AUTH_USER_MODEL, verbose_name='user_chapter_status'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chapters', to='courses.course', verbose_name='Курс'),
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
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('user', 'course'), name='unique_user_course'),
        ),
        migrations.AddConstraint(
            model_name='lesson',
            constraint=models.UniqueConstraint(fields=('order_number', 'chapter'), name='unique_lesson_order_number'),
        ),
        migrations.AddConstraint(
            model_name='knowledge',
            constraint=models.UniqueConstraint(fields=('title',), name='unique_knowledge'),
        ),
        migrations.AddConstraint(
            model_name='chapter',
            constraint=models.UniqueConstraint(fields=('order_number', 'course'), name='unique_order_number'),
        ),
    ]