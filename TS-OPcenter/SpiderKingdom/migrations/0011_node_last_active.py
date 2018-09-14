# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-23 12:01
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SpiderKingdom', '0010_auto_20180822_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='last_active',
            field=models.DateTimeField(default=datetime.datetime.now, help_text='最后活动时间', verbose_name='最后活动时间'),
        ),
    ]
