# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-06 07:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SpiderKingdom', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='monitordata',
            old_name='url',
            new_name='domain',
        ),
    ]
