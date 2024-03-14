# Generated by Django 3.2.23 on 2024-03-13 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeworks', '0002_alter_homework_lesson'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='homework',
            constraint=models.UniqueConstraint(fields=('subscription', 'lesson'), name='unique_subscription_lesson'),
        ),
    ]