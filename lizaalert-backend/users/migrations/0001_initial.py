# Generated by Django 4.0.6 on 2023-01-30 15:40

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import easy_thumbnails.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('patronymic', models.CharField(blank=True, max_length=20, verbose_name='Отчество')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Наименование значка')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание значка и условий его получения')),
            ],
            options={
                'verbose_name': 'Значок',
                'verbose_name_plural': 'Значки',
                'db_table': 'badges',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='Наименование направления')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание направления')),
            ],
            options={
                'verbose_name': 'Направление',
                'verbose_name_plural': 'Направления',
                'db_table': 'departments',
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Новичок', 'novice'), ('Бывалый', 'experienced'), ('Профессионал', 'professional')], max_length=20, verbose_name='Наименование уровня')),
                ('description', models.TextField(verbose_name='Описание уровня и условия его достижения')),
            ],
            options={
                'verbose_name': 'Уровень',
                'verbose_name_plural': 'Уровни',
                'db_table': 'levels',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Код региона')),
                ('region', models.CharField(max_length=120, verbose_name='Наименование региона')),
            ],
            options={
                'verbose_name': 'Регион',
                'verbose_name_plural': 'Регионы',
                'db_table': 'locations',
            },
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, verbose_name='Номер телефона')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('call_sign', models.CharField(blank=True, max_length=50, null=True, verbose_name='Позывной на форуме')),
                ('photo', easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='', verbose_name='Путь к фотографии')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания запси')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления записи')),
            ],
            options={
                'verbose_name': 'Волонтер',
                'verbose_name_plural': 'Волонтеры',
                'db_table': 'volunteers',
            },
        ),
        migrations.CreateModel(
            name='VolunteerLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmed', models.BooleanField(default=False, verbose_name='Статус подтверждения уровня')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level_volunteers', to='users.level', verbose_name='Уровень')),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volunteer_levels', to='users.volunteer', verbose_name='Волонтер')),
                ('who_confirmed', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Кто подтвердил статус')),
            ],
            options={
                'verbose_name': 'Уровень волонтера',
                'verbose_name_plural': 'Уровни волонтеров',
                'db_table': 'volunteers_levels',
            },
        ),
        migrations.CreateModel(
            name='VolunteerCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assessment', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)], verbose_name='Оценка за курс')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время записи на курс')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_volunteers', to='courses.course', verbose_name='Курс')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='volunteer_courses', to='courses.coursestatus', verbose_name='Статус')),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volunter_courses', to='users.volunteer', verbose_name='Волонтер')),
            ],
            options={
                'verbose_name': 'Курс волонтера',
                'verbose_name_plural': 'Курсы волонтеров',
                'db_table': 'volunteers_courses',
            },
        ),
        migrations.CreateModel(
            name='VolunteerBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='badge_volunteers', to='users.badge', verbose_name='Значок')),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volunteer_badges', to='users.volunteer', verbose_name='Волонтер')),
            ],
            options={
                'verbose_name': 'Значок волонтера',
                'verbose_name_plural': 'Значки волонтеров',
                'db_table': 'volunteers_badges',
            },
        ),
        migrations.AddField(
            model_name='volunteer',
            name='badges',
            field=models.ManyToManyField(blank=True, null=True, related_name='volunteers', through='users.VolunteerBadge', to='users.badge', verbose_name='Значки'),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='courses',
            field=models.ManyToManyField(blank=True, related_name='volunteers', through='users.VolunteerCourse', to='courses.course', verbose_name='Курсы'),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='volunteers', to='users.department', verbose_name='Направление'),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='level',
            field=models.ManyToManyField(blank=True, null=True, related_name='volunteers', through='users.VolunteerLevel', to='users.level', verbose_name='Уровень'),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='volunteers', to='users.location', verbose_name='Географический регион'),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='user',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('main admin', 'Главный Администратор'), ('admin', 'Администратор'), ('teacher', 'Преподаватель'), ('volunteer', 'Волонтёр')], max_length=20, verbose_name='Роль пользователя')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Роль пользователя',
                'verbose_name_plural': 'Роли пользователей',
            },
        ),
        migrations.AddConstraint(
            model_name='volunteerlevel',
            constraint=models.UniqueConstraint(fields=('volunteer', 'level'), name='unique_volunteer_level'),
        ),
        migrations.AddConstraint(
            model_name='volunteercourse',
            constraint=models.UniqueConstraint(fields=('volunteer', 'course', 'status'), name='unique_volunteer_course'),
        ),
        migrations.AddConstraint(
            model_name='userrole',
            constraint=models.UniqueConstraint(fields=('user', 'role'), name='unique_user_role'),
        ),
    ]
