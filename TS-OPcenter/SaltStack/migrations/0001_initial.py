# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-20 14:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Groups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='DefaultGroup', help_text='分组名称', max_length=32, unique=True, verbose_name='分组名称')),
                ('description', models.CharField(blank=True, help_text='组描述', max_length=32, null=True, verbose_name='组描述')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, help_text='添加时间', verbose_name='添加时间')),
            ],
            options={
                'verbose_name_plural': '主机分组',
            },
        ),
        migrations.CreateModel(
            name='Jobs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(help_text='任务自编码', max_length=11, unique=True, verbose_name='任务自编码')),
                ('status', models.IntegerField(choices=[(0, '排队中'), (1, '执行中'), (2, '已完成'), (3, '异常')], default=0, help_text='任务状态', verbose_name='任务状态')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='任务创建时间', verbose_name='任务创建时间')),
                ('targets_total', models.IntegerField(default=0, help_text='目标主机总数', verbose_name='目标主机总数量')),
                ('jid', models.CharField(blank=True, help_text='任务系统编码', max_length=20, null=True, verbose_name='任务系统编码')),
                ('start_time', models.DateTimeField(blank=True, help_text='任务开始时间', null=True, verbose_name='任务开始时间')),
                ('finish_time', models.DateTimeField(blank=True, help_text='任务结束时间', null=True, verbose_name='任务结束时间')),
                ('information', models.TextField(blank=True, help_text='任务详情', null=True, verbose_name='任务详情')),
                ('success_total', models.IntegerField(default=0, help_text='执行成功主机数量', null=True, verbose_name='执行成功主机数量')),
            ],
        ),
        migrations.CreateModel(
            name='Minions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minion_id', models.CharField(help_text='客户端的minion_id', max_length=32, unique=True, verbose_name='客户端的minion_id')),
                ('ipv4', models.CharField(help_text='IP地址', max_length=20, unique=True, verbose_name='IP地址')),
                ('city', models.CharField(help_text='所在城市', max_length=20, verbose_name='所在城市')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, help_text='添加时间', verbose_name='添加时间')),
                ('jobs_count', models.IntegerField(default=0, help_text='本机执行剧本次数', null=True, verbose_name='本机执行剧本次数')),
                ('test_time', models.DateTimeField(blank=True, help_text='最后一次检测时间', null=True, verbose_name='最后一次检测时间')),
                ('online_time', models.DateTimeField(blank=True, help_text='最后在线的时间', null=True, verbose_name='最后在线的时间')),
                ('status', models.IntegerField(choices=[(0, '离线'), (1, '在线'), (2, '检测中')], default=2, help_text='联机状态', verbose_name='联机状态')),
                ('osfinger', models.CharField(blank=True, help_text='操作系统类型', max_length=32, null=True, verbose_name='操作系统类型')),
                ('cpu_model', models.CharField(blank=True, help_text='CPU型号', max_length=64, null=True, verbose_name='CPU型号')),
                ('num_cpus', models.IntegerField(blank=True, help_text='CPU配置', null=True, verbose_name='CPU配置')),
                ('mem_total', models.IntegerField(blank=True, help_text='实际内存', null=True, verbose_name='实际内存')),
                ('mem_gib', models.CharField(blank=True, help_text='内存配置', max_length=10, null=True, verbose_name='内存配置')),
                ('group', models.ManyToManyField(help_text='所属分组', to='SaltStack.Groups', verbose_name='所属分组')),
            ],
            options={
                'verbose_name_plural': '主机列表',
            },
        ),
        migrations.CreateModel(
            name='Playbooks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(help_text='剧本功能描述', max_length=28, verbose_name='第二行注释，剧本功能描述')),
                ('context', models.TextField(help_text='剧本上下文', verbose_name='剧本上下文')),
                ('lines', models.IntegerField(default=0, help_text='剧本内容总行数', verbose_name='剧本内容总行数')),
                ('status', models.BooleanField(default=True, help_text='剧本状态', verbose_name='剧本状态')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, help_text='添加时间', verbose_name='添加时间')),
                ('update_time', models.DateTimeField(default=django.utils.timezone.now, help_text='添加时间', verbose_name='添加时间')),
                ('group', models.ForeignKey(help_text='剧本所属分组', on_delete=django.db.models.deletion.CASCADE, to='SaltStack.Groups', verbose_name='第一行注释，剧本所属分组')),
            ],
            options={
                'verbose_name_plural': '使用中的剧本',
            },
        ),
        migrations.CreateModel(
            name='Playbooks_previous',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change', models.CharField(default='', help_text='修改说明', max_length=100, verbose_name='修改说明')),
                ('description', models.CharField(help_text='剧本功能描述', max_length=28, verbose_name='第二行注释，剧本功能描述')),
                ('context', models.TextField(help_text='剧本上下文', verbose_name='剧本上下文')),
                ('lines', models.IntegerField(default=0, help_text='剧本内容总行数', verbose_name='剧本内容总行数')),
                ('update_time', models.DateTimeField(default=django.utils.timezone.now, help_text='添加时间', verbose_name='添加时间')),
                ('release', models.ForeignKey(help_text='关联的剧本', on_delete=django.db.models.deletion.CASCADE, to='SaltStack.Playbooks', verbose_name='关联的剧本')),
            ],
            options={
                'verbose_name_plural': '剧本版本管理',
            },
        ),
        migrations.AddField(
            model_name='jobs',
            name='description',
            field=models.ForeignKey(help_text='任务描述', on_delete=django.db.models.deletion.CASCADE, to='SaltStack.Playbooks', verbose_name='任务描述'),
        ),
        migrations.AddField(
            model_name='jobs',
            name='group',
            field=models.ForeignKey(help_text='所属分组', on_delete=django.db.models.deletion.CASCADE, to='SaltStack.Groups', verbose_name='所属分组'),
        ),
        migrations.AddField(
            model_name='jobs',
            name='minions',
            field=models.ManyToManyField(help_text='受影响主机', to='SaltStack.Minions', verbose_name='受影响主机'),
        ),
    ]