# Generated by Django 3.2.20 on 2023-10-27 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20230811_1615'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='volunteercourse',
            name='unique_volunteer_course',
        ),
        migrations.RemoveField(
            model_name='volunteercourse',
            name='status',
        ),
        migrations.AddConstraint(
            model_name='volunteercourse',
            constraint=models.UniqueConstraint(fields=('volunteer', 'course'), name='unique_volunteer_course'),
        ),
    ]
