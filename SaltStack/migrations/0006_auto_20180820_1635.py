# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-20 16:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SaltStack', '0005_auto_20180820_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playbooks',
            name='description',
            field=models.CharField(help_text='剧本功能描述', max_length=28, unique=True, verbose_name='第二行注释，剧本功能描述'),
        ),
    ]
