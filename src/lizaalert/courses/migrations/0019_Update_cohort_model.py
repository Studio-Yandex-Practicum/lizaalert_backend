# Generated by Django 3.2.20 on 2024-01-19 16:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0018_auto_20240119_1504'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cohort',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('cohort_number', models.PositiveIntegerField(verbose_name='Номер группы')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Дата начала')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата окончания')),
                ('students_count', models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество студентов')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cohorts', to='courses.course', verbose_name='Курс')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Преподаватель')),
            ],
            options={
                'verbose_name': 'Группа курса',
                'verbose_name_plural': 'Группы курса',
            },
        ),
        migrations.AddField(
            model_name='subscription',
            name='cohort',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='courses.cohort', verbose_name='Группа'),
        ),
        migrations.AddConstraint(
            model_name='cohort',
            constraint=models.UniqueConstraint(fields=('course', 'cohort_number'), name='unique_course_cohort_number'),
        ),
    ]