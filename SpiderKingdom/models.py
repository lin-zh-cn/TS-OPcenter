import datetime

from django.db import models

# Create your models here.
class Node(models.Model):
    online_choice = ((0,'在线'),(1,'离线'),)
    node = models.CharField(max_length=20, unique=True, verbose_name="节点名称", help_text="节点名称")
    ip = models.CharField(max_length=20,blank=True,null=True,verbose_name="节点IP", help_text="节点IP")
    description = models.CharField(max_length=4096,blank=True,null=True,verbose_name="节点描述", help_text="节点名称")
    online= models.IntegerField(default=0,choices=online_choice,verbose_name="在线状态", help_text="在线状态，0=在线，1=离线(缺省值：0)")
    last_active= models.DateTimeField(default=datetime.datetime.now,verbose_name="最后活动时间", help_text="最后活动时间")
    add_time = models.DateTimeField(default=datetime.datetime.now,verbose_name="添加时间", help_text="添加时间(缺省值：当前时间)")

    def __str__(self):
        return self.node
    class Meta:
        verbose_name_plural = "检测节点"

class Project(models.Model):
    name = models.CharField(max_length=20,unique=True,null=True,verbose_name="项目名称", help_text="项目名称")
    add_time = models.DateTimeField(default=datetime.datetime.now, verbose_name="添加时间", help_text="添加时间(缺省值：当前时间)")
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "项目"

class CDN(models.Model):
    cdn = models.CharField(null=True, default=None, max_length=60,verbose_name="CDN厂商名称", help_text="CDN厂商名称")
    add_time = models.DateTimeField(default=datetime.datetime.now, verbose_name="添加时间", help_text="添加时间(缺省值：当前时间)")
    def __str__(self):
        return self.cdn
    class Meta:
        verbose_name_plural = "CDN厂商"

class Domain(models.Model):
    # check_id_choice = (
    #     (0,'检查'),
    #     (1,'不检查'),
    # )
    #
    # warning_choice = (
    #     (0,'警告'),
    #     (1,'不警告')
    # )
    domain = models.CharField(max_length=60,unique=True,verbose_name="域名", help_text="域名")
    project = models.ForeignKey('Project',blank=True,null=True,verbose_name="项目", help_text="项目ID")
    status = models.ForeignKey('StatusCode',to_field='id',default=1,verbose_name="域名状态", help_text="域名状态ID(缺省值：1，OK)")
    cert_valid_date = models.CharField(null=True,blank=True,max_length=20,verbose_name="证书有效期", help_text="证书有效期")
    cert_valid_days = models.IntegerField(null=True,blank=True,verbose_name="证书剩余天数", help_text="证书剩余天数")
    check = models.BooleanField(default=True,verbose_name="是否检查", help_text="是否检查True/False(缺省值：True)")
    warning = models.BooleanField(default=True,verbose_name="是否警告", help_text="是否警告True/False(缺省值：True)")
    cdn = models.ForeignKey('CDN',blank=True,null=True,verbose_name="CDN厂商", help_text="CDN厂商ID")
    detection_interval = models.IntegerField(default=300,verbose_name="检查间隔", help_text="检查间隔，秒(缺省值：300)")
    trigger = models.IntegerField(default=1,verbose_name="连续异常几次才警告", help_text="连续异常几次才警告(缺省值：1)")
    nodes = models.ManyToManyField('Node',blank=True,verbose_name="节点", help_text="检测节点ID")
    add_time = models.DateTimeField(default=datetime.datetime.now, verbose_name="添加时间", help_text="添加时间(缺省值：当前时间)")

    def __str__(self):
        return self.domain

    class Meta:
        verbose_name_plural = "域名信息"

class MonitorData(models.Model):
    node = models.ForeignKey('Node',verbose_name="节点名称", help_text="节点ID")
    domain = models.ForeignKey('Domain',verbose_name="域名", help_text="域名ID")
    http_code = models.IntegerField(blank=True,null=True,verbose_name="http状态码", help_text="http请求状态码")
    total_time = models.IntegerField(blank=True,null=True,verbose_name="请求耗时", help_text="请求耗时")
    datetime = models.DateTimeField(db_index=True,verbose_name="检测时间", help_text="检测时间")
    detection_interval = models.IntegerField(default=300, verbose_name="检查间隔", help_text="检查间隔，秒(缺省值：300)")

    class Meta:
        verbose_name_plural = "检测数据"


class StatusCode(models.Model):
    status_code = models.IntegerField(unique=True,verbose_name="状态码", help_text="状态码")
    status_description = models.CharField(max_length=60,unique=True,verbose_name="状态描述", help_text="状态描述")
    add_time = models.DateTimeField(default=datetime.datetime.now, verbose_name="添加时间", help_text="添加时间(缺省值：当前时间)")

    def __str__(self):
        return self.status_description
    class Meta:
        verbose_name_plural = "状态码"

class FailLog(models.Model):
    node = models.ForeignKey('Node',blank=True,null=True,verbose_name="节点", help_text="节点ID")
    domain = models.ForeignKey('Domain',blank=True,null=True,verbose_name="域名", help_text="域名ID")
    datetime = models.DateTimeField()