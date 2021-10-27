# Generated by Django 3.2.8 on 2021-10-27 01:44

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('type', models.CharField(max_length=2000, null=True)),
                ('userId', models.CharField(max_length=2000, null=True)),
                ('host', models.CharField(max_length=2000, null=True)),
                ('displayName', models.CharField(max_length=2000, null=True)),
                ('url', models.URLField(max_length=2000, null=True)),
                ('github', models.URLField(max_length=2000, null=True)),
                ('profileImage', models.URLField(max_length=2000, null=True)),
                ('followList', models.JSONField(null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
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
            name='Liked',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=2000)),
                ('itmes', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('context', models.URLField()),
                ('summary', models.CharField(max_length=2000)),
                ('type', models.CharField(max_length=2000)),
                ('author', models.JSONField()),
                ('object', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Moment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=2000, null=True)),
                ('title', models.CharField(max_length=2000, null=True)),
                ('momentId', models.CharField(max_length=2000, null=True)),
                ('source', models.CharField(max_length=2000, null=True)),
                ('origin', models.CharField(max_length=2000, null=True)),
                ('description', models.CharField(max_length=2000, null=True)),
                ('contentTyep', models.CharField(max_length=2000, null=True)),
                ('content', models.CharField(max_length=2000, null=True)),
                ('categories', models.JSONField(null=True)),
                ('count', models.PositiveIntegerField(null=True)),
                ('comments', models.URLField(null=True)),
                ('commentsSrc', models.JSONField(null=True)),
                ('published', models.DateTimeField(null=True)),
                ('visibility', models.CharField(max_length=2000, null=True)),
                ('unlisted', models.BooleanField(null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='moment', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=2000)),
                ('items', models.JSONField()),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=2000, null=True)),
                ('author', models.JSONField(null=True)),
                ('content', models.CharField(max_length=2000, null=True)),
                ('contentType', models.CharField(max_length=2000, null=True)),
                ('published', models.DateTimeField(null=True)),
                ('commentId', models.CharField(max_length=2000, null=True)),
                ('complete', models.BooleanField(null=True)),
                ('moment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.moment')),
            ],
        ),
    ]
