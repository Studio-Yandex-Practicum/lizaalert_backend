# Generated by Django 3.2.23 on 2024-02-21 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0026_alter_lesson_lesson_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Webinar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Draft'), (3, 'APPROVED')], default=0, verbose_name='Статус')),
                ('link', models.CharField(max_length=400, verbose_name='Ссылка на вебинар')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webinar', to='courses.lesson', verbose_name='Урок')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.subscription', verbose_name='Подписка')),
            ],
            options={
                'verbose_name': 'Вебинар',
                'verbose_name_plural': 'Вебинары',
                'ordering': ['-updated_at'],
            },
        ),
    ]
