# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime

def convert_subscription(apps, schema_editor):
    User = apps.get_model("users.User")
    for user in User.objects.all():
        if user.subscribed_to_notification_emails:
            # Set to default of 3 days
            user.email_notification_frequency = 3
            user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_notification_frequency',
            field=models.IntegerField(default=3, choices=[('Every 3 days', 3), ('Weekly', 7), ('Never', 0)], verbose_name='days between email notifications'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='last_notification_email',
            field=models.DateField(default=datetime.datetime.now, auto_now_add=True, verbose_name='last notification emaildate'),
            preserve_default=True,
        ),
        migrations.RunPython(convert_subscription),
        migrations.RemoveField(
            model_name='user',
            name='subscribed_to_notification_emails',
        ),
    ]
