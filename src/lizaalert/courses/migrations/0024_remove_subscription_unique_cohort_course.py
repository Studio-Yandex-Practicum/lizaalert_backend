# Generated by Django 3.2.23 on 2024-02-14 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0023_auto_20240212_1755'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscription',
            name='unique_cohort_course',
        ),
    ]
