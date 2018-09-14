# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-09 12:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SpiderKingdom', '0006_monitordata_detection_interval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cdn',
            name='add_time',
            field=models.DateTimeField(default=datetime.datetime.now, help_text='添加时间(缺省值：当前时间)', verbose_name='添加时间'),
        ),
        migrations.AlterField(
            model_name='cdn',
            name='cdn',
            field=models.CharField(default=None, help_text='CDN厂商名称', max_length=60, null=True, verbose_name='CDN厂商名称'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='add_time',
            field=models.DateTimeField(default=datetime.datetime.now, help_text='添加时间(缺省值：当前时间)', verbose_name='添加时间'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='cdn',
            field=models.ForeignKey(blank=True, help_text='CDN厂商ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='SpiderKingdom.CDN', verbose_name='CDN厂商'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='cert_valid_date',
            field=models.CharField(blank=True, help_text='证书有效期', max_length=20, null=True, verbose_name='证书有效期'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='cert_valid_days',
            field=models.IntegerField(blank=True, help_text='证书剩余天数', null=True, verbose_name='证书剩余天数'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='check',
            field=models.BooleanField(default=True, help_text='是否检查True/False(缺省值：True)', verbose_name='是否检查'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='detection_interval',
            field=models.IntegerField(default=300, help_text='检查间隔，秒(缺省值：300)', verbose_name='检查间隔'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='domain',
            field=models.CharField(help_text='域名', max_length=60, unique=True, verbose_name='域名'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='nodes',
            field=models.ManyToManyField(help_text='检测节点ID', to='SpiderKingdom.Node', verbose_name='节点'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='project',
            field=models.ForeignKey(blank=True, help_text='项目ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='SpiderKingdom.Project', verbose_name='项目'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='status',
            field=models.ForeignKey(default=1, help_text='域名状态ID(缺省值：1，OK)', on_delete=django.db.models.deletion.CASCADE, to='SpiderKingdom.StatusCode', verbose_name='域名状态'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='trigger',
            field=models.IntegerField(default=1, help_text='连续异常几次才警告(缺省值：1)', verbose_name='连续异常几次才警告'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='warning',
            field=models.BooleanField(default=True, help_text='是否警告True/False(缺省值：True)', verbose_name='是否警告'),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='domain',
            field=models.ForeignKey(blank=True, help_text='域名ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='SpiderKingdom.Domain', verbose_name='域名'),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='event_type',
            field=models.ForeignKey(blank=True, help_text='错误状态ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='SpiderKingdom.StatusCode', verbose_name='状态描述'),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='node',
            field=models.ForeignKey(blank=True, help_text='节点ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='SpiderKingdom.Node', verbose_name='节点'),
        ),
        migrations.AlterField(
            model_name='monitordata',
            name='datetime',
            field=models.DateTimeField(db_index=True, help_text='检测时间', verbose_name='检测时间'),
        ),
        migrations.AlterField(
            model_name='monitordata',
            name='detection_interval',
            field=models.IntegerField(default=300, help_text='检查间隔，秒(缺省值：300)', verbose_name='检查间隔'),
        ),
        migrations.AlterField(
            model_name='monitordata',
            name='domain',
            field=models.ForeignKey(help_text='域名ID', on_delete=django.db.models.deletion.CASCADE, to='SpiderKingdom.Domain', verbose_name='域名'),
        ),
        migrations.AlterField(
            model_name='monitordata',
            name='http_code',
            field=models.IntegerField(blank=True, help_text='http请求状态码', null=True, verbose_name='http状态码'),
        ),
        migrations.AlterField(
            model_name='monitordata',
            name='node',
            field=models.ForeignKey(help_text='节点ID', on_delete=django.db.models.deletion.CASCADE, to='SpiderKingdom.Node', verbose_name='节点名称'),
        ),
        migrations.AlterField(
            model_name='monitordata',
            name='total_time',
            field=models.IntegerField(blank=True, help_text='请求耗时', null=True, verbose_name='请求耗时'),
        ),
        migrations.AlterField(
            model_name='node',
            name='add_time',
            field=models.DateTimeField(default=datetime.datetime.now, help_text='添加时间(缺省值：当前时间)', verbose_name='添加时间'),
        ),
        migrations.AlterField(
            model_name='node',
            name='description',
            field=models.CharField(blank=True, help_text='节点名称', max_length=4096, null=True, verbose_name='节点描述'),
        ),
        migrations.AlterField(
            model_name='node',
            name='ip',
            field=models.CharField(blank=True, help_text='节点IP', max_length=20, null=True, verbose_name='节点IP'),
        ),
        migrations.AlterField(
            model_name='node',
            name='node',
            field=models.CharField(help_text='节点名称', max_length=20, unique=True, verbose_name='节点名称'),
        ),
        migrations.AlterField(
            model_name='node',
            name='online',
            field=models.IntegerField(choices=[(0, '在线'), (1, '离线')], default=0, help_text='在线状态，0=在线，1=离线(缺省值：0)', verbose_name='在线状态'),
        ),
        migrations.AlterField(
            model_name='project',
            name='add_time',
            field=models.DateTimeField(default=datetime.datetime.now, help_text='添加时间(缺省值：当前时间)', verbose_name='添加时间'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(help_text='项目名称', max_length=20, null=True, unique=True, verbose_name='项目名称'),
        ),
        migrations.AlterField(
            model_name='statuscode',
            name='add_time',
            field=models.DateTimeField(default=datetime.datetime.now, help_text='添加时间(缺省值：当前时间)', verbose_name='添加时间'),
        ),
        migrations.AlterField(
            model_name='statuscode',
            name='status_code',
            field=models.IntegerField(help_text='状态码', unique=True, verbose_name='状态码'),
        ),
        migrations.AlterField(
            model_name='statuscode',
            name='status_description',
            field=models.CharField(help_text='状态描述', max_length=60, unique=True, verbose_name='状态描述'),
        ),
    ]