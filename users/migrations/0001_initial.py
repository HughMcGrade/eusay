# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('tags', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')], verbose_name='username', max_length=30)),
                ('first_name', models.CharField(verbose_name='first name', blank=True, max_length=30)),
                ('last_name', models.CharField(verbose_name='last name', blank=True, max_length=30)),
                ('email', models.EmailField(verbose_name='email address', blank=True, max_length=75)),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', verbose_name='staff status', default=False)),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active', default=True)),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('sid', models.CharField(unique=True, verbose_name='student ID', max_length=20)),
                ('slug', models.SlugField(default='slug')),
                ('userStatus', models.CharField(choices=[('User', 'Regular User'), ('Staff', 'EUSA Staff'), ('Candidate', 'EUSA Candidate'), ('Officeholder', 'EUSA Officeholder')], verbose_name='user status', default='User', max_length=12)),
                ('title', models.CharField(blank=True, max_length=100)),
                ('isModerator', models.BooleanField(verbose_name='moderator', default=False)),
                ('hasProfile', models.BooleanField(verbose_name='public profile', default=False)),
                ('subscribed_to_notification_emails', models.BooleanField(verbose_name='subscribed to notification emails?', default=True)),
                ('follows_tags', models.ManyToManyField(blank=True, related_name='followers', to='tags.Tag')),
                ('groups', models.ManyToManyField(related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups', related_name='user_set', blank=True, to='auth.Group')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', help_text='Specific permissions for this user.', verbose_name='user permissions', related_name='user_set', blank=True, to='auth.Permission')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
