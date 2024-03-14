# Generated by Django 3.2.23 on 2024-03-13 10:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0028_auto_20240313_1341'),
        ('users', '0008_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='courses.division', verbose_name='Направление умения'),
        ),
        migrations.AddConstraint(
            model_name='badge',
            constraint=models.UniqueConstraint(fields=('name', 'division'), name='unique_badge'),
        ),
    ]