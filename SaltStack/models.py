from django.db import models
import datetime
from django.utils import timezone
# Create your models here.

# 分组管理
class Groups(models.Model):
    name = models.CharField(max_length=32, unique=True, default="DefaultGroup", null=False, verbose_name="分组名称", help_text="分组名称")
    description = models.CharField(max_length=32, null=True, blank=True, verbose_name="组描述", help_text="组描述")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间", help_text="添加时间")
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "主机分组"

# 主机管理
class Minions(models.Model):
    status_choice = ( (0,'离线'), (1,'在线'), (2,'检测中'), (3,'异常'), )
    minion_id = models.CharField(max_length=32, unique=True, null=False, verbose_name="客户端的minion_id", help_text="客户端的minion_id")
    ip = models.GenericIPAddressField(unique=True, null=False, verbose_name="IP地址", help_text="IP地址")
    city = models.CharField(max_length=20, null=False, verbose_name="所在城市", help_text="所在城市")
    group = models.ManyToManyField('Groups', verbose_name="所属分组", help_text="所属分组")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间", help_text="添加时间")
    jobs_count = models.IntegerField(null=True, default=0, verbose_name="本机执行剧本次数", help_text="本机执行剧本次数")
    last_test = models.DateTimeField(null=True, blank=True, verbose_name="最后一次检测时间", help_text="最后一次检测时间")
    last_online = models.DateTimeField(null=True, blank=True, verbose_name="最后在线的时间", help_text="最后在线的时间")
    status = models.IntegerField(choices=status_choice, default=2, null=False, verbose_name="联机状态", help_text="联机状态")
    osfinger = models.CharField(max_length=32, null=True, blank=True, verbose_name="操作系统类型", help_text="操作系统类型")
    cpu_model = models.CharField(max_length=64, null=True, blank=True, verbose_name="CPU型号", help_text="CPU型号")
    num_cpus = models.IntegerField(null=True, blank=True, verbose_name="CPU配置", help_text="CPU配置")
    mem_total = models.IntegerField(null=True, blank=True, verbose_name="实际内存", help_text="实际内存")
    mem_gib = models.CharField(max_length=10,null=True, blank=True, verbose_name="内存配置", help_text="内存配置")
    def __str__(self):
        return self.minion_id
    class Meta:
        verbose_name_plural = "主机列表"

# 使用中的剧本
class Playbooks(models.Model):
    # Linux
    # Linux系统初始化
    # 上传剧本，文件内容第一行注释是剧本所属组，第二行注释是剧本描述。组必须已经存在，组在admin后台设置。
    #
    #status_choice = ((0, '可用'), (1, '禁用'),)
    group = models.ForeignKey('Groups', verbose_name="第一行注释，剧本所属分组", help_text="剧本所属分组")
    description = models.CharField(max_length=28, unique=True, null=False, verbose_name="第二行注释，剧本功能描述", help_text="剧本功能描述")
    context = models.TextField(null=False, verbose_name="剧本上下文", help_text="剧本上下文")
    lines = models.IntegerField(null=False, default=0, verbose_name="剧本内容总行数", help_text="剧本内容总行数")
    status = models.BooleanField(default=True, null=False, verbose_name="剧本状态", help_text="剧本状态")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间", help_text="添加时间")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间", help_text="添加时间")
    def __str__(self):
        return self.description
    class Meta:
        verbose_name_plural = "使用中的剧本"

# 剧本历史版本
class Playbooks_previous(models.Model):
    # Linux
    # Linux系统初始化
    # 上传剧本，文件内容第一行注释是剧本所属组，第二行注释是剧本描述。组必须已经存在，组在admin后台设置。
    #
    release = models.ForeignKey(Playbooks, to_field="id", verbose_name="关联的剧本", help_text="关联的剧本")
    description = models.CharField(max_length=28, null=False, verbose_name="第二行注释，剧本功能描述", help_text="剧本功能描述")
    context = models.TextField(null=False, verbose_name="剧本上下文", help_text="剧本上下文")
    lines = models.IntegerField(null=False, default=0, verbose_name="剧本内容总行数", help_text="剧本内容总行数")
    change = models.CharField(max_length=100, null=True, blank=True, default='', verbose_name="修改说明", help_text="修改说明")
    update_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间", help_text="添加时间")
    def __str__(self):
        return self.release
    class Meta:
        verbose_name_plural = "剧本版本管理"

# 执行剧本任务日志
class Jobs(models.Model):
    async_jobs_stauts = ((0,'排队中'), (1,'执行中'), (2,'已完成'), (3,'异常'), )
    # 执行流程和状态描述
    status = models.IntegerField(choices=async_jobs_stauts,default=0, verbose_name="任务当前状态", help_text="任务当前状态")
    number = models.CharField(max_length=11, unique=True, null=False, verbose_name="任务自编码", help_text="任务自编码")
    group = models.ForeignKey('Groups', verbose_name="所属分组", help_text="所属分组")
    minions = models.ManyToManyField('Minions', verbose_name="受影响主机", help_text="受影响主机")
    description = models.ForeignKey('Playbooks', verbose_name="任务描述", help_text="任务描述")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="任务创建时间", help_text="任务创建时间")
    targets_total = models.IntegerField(null=False,default=0, verbose_name="目标主机总数量", help_text="目标主机总数")
    # 执行任务分析数据
    jid = models.CharField(max_length=20,null=True,blank=True, verbose_name="任务系统编码", help_text="任务系统编码")
    start_time = models.DateTimeField(null=True,blank=True, verbose_name="任务开始时间", help_text="任务开始时间")
    finish_time = models.DateTimeField(null=True,blank=True, verbose_name="任务结束时间", help_text="任务结束时间")
    information = models.TextField(null=True,blank=True, verbose_name="任务详情", help_text="任务详情")
    success_total = models.IntegerField(null=True,default=0, verbose_name="执行成功主机数量", help_text="执行成功主机数量")

