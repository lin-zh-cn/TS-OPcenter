# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-22 10:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SaltStack', '0008_auto_20180822_1013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobs',
            name='status_flow',
        ),
    ]
