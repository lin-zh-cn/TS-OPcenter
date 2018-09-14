from django.contrib import admin

# Register your models here.
from SpiderKingdom.models import Project
from SpiderKingdom.models import Domain
from SpiderKingdom.models import StatusCode
from SpiderKingdom.models import Node
from SpiderKingdom.models import CDN

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id','name']
    ordering = ('id',)

@admin.register(CDN)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id','cdn']
    list_display_links = ['cdn']
    ordering = ('id',)

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display_links = ['domain']
    filter_horizontal = ['nodes',]

    list_display = ['id','domain','project','status','check','warning','cert_valid_date','cert_valid_days','cdn','detection_interval','trigger']

@admin.register(StatusCode)
class StatusCodeAdmin(admin.ModelAdmin):
    list_display = ['status_code','status_description']
    list_display_links = ['status_code','status_description']
    ordering = ('id',)


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ['id','node','ip','description','online']
    list_display_links = ['node']
    ordering = ('id',)