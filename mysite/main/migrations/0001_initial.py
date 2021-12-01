# Generated by Django 3.1.6 on 2021-12-01 20:26

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import main.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
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
                ('id', models.CharField(default=main.models.createUUID, max_length=2000, primary_key=True, serialize=False)),
                ('localId', models.CharField(max_length=2000, null=True)),
                ('host', models.CharField(max_length=2000, null=True)),
                ('displayName', models.CharField(max_length=2000, null=True)),
                ('url', models.URLField(max_length=2000, null=True)),
                ('github', models.URLField(max_length=2000, null=True)),
                ('profileImage', models.URLField(max_length=2000, null=True)),
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
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=2000, null=True)),
                ('content', models.CharField(max_length=2000, null=True)),
                ('contentType', models.CharField(max_length=2000, null=True)),
                ('published', models.DateTimeField(null=True)),
                ('commentId', models.CharField(max_length=2000, null=True)),
                ('localId', models.CharField(max_length=2000, null=True)),
                ('complete', models.BooleanField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Following',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=2000)),
                ('items', models.JSONField()),
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
                ('userId', models.CharField(max_length=2000)),
            ],
        ),
        migrations.CreateModel(
            name='Moment',
            fields=[
                ('type', models.CharField(max_length=2000, null=True)),
                ('title', models.CharField(max_length=2000, null=True)),
                ('id', models.CharField(max_length=2000, primary_key=True, serialize=False)),
                ('localId', models.CharField(max_length=2000)),
                ('source', models.CharField(max_length=2000, null=True)),
                ('origin', models.CharField(max_length=2000, null=True)),
                ('description', models.CharField(max_length=2000, null=True)),
                ('contentType', models.CharField(max_length=2000, null=True)),
                ('content', models.CharField(max_length=10485760, null=True)),
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
        migrations.AddConstraint(
            model_name='likes',
            constraint=models.UniqueConstraint(fields=('userId', 'object'), name='like constraint'),
        ),
        migrations.AddField(
            model_name='inbox',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='following',
            name='following_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followed', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='following',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='moment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.moment'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AddConstraint(
            model_name='following',
            constraint=models.UniqueConstraint(fields=('user', 'following_user'), name='follow constraint'),
        ),
    ]
