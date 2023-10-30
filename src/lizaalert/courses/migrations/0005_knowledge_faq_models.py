# Generated by Django 3.2.20 on 2023-08-31 08:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0004_course_faq'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='faq',
        ),
        migrations.RemoveField(
            model_name='course',
            name='knowledge',
        ),
        migrations.CreateModel(
            name='Knowledge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=250, verbose_name='Название умения')),
                ('description', models.CharField(max_length=1000, verbose_name='Описание умения')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Создатель умения')),
            ],
            options={
                'verbose_name': 'Умение',
                'verbose_name_plural': 'Умения',
            },
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.CharField(max_length=250, verbose_name='Вопрос')),
                ('answer', models.CharField(max_length=1000, verbose_name='Ответ')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Создатель вопроса')),
            ],
            options={
                'verbose_name': 'FAQ',
                'verbose_name_plural': 'FAQ',
            },
        ),
        migrations.CreateModel(
            name='CourseKnowledge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='courses.course')),
                ('knowledge', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='courses.knowledge')),
            ],
            options={
                'ordering': ('knowledge',),
            },
        ),
        migrations.CreateModel(
            name='CourseFaq',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='courses.course')),
                ('faq', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='courses.faq')),
            ],
            options={
                'ordering': ('faq',),
            },
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
        migrations.AddConstraint(
            model_name='knowledge',
            constraint=models.UniqueConstraint(fields=('title',), name='unique_knowledge'),
        ),
    ]