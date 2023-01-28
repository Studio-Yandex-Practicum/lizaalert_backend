# Generated by Django 3.2.12 on 2022-07-10 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_coursestatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursestatus',
            name='slug',
            field=models.CharField(choices=[('active', 'Active'), ('complete', 'Complete'), ('registration', 'Registration')], default='active', editable=False, max_length=20),
        ),
    ]
