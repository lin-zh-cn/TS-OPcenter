from django.contrib.auth.models import User, Group
from SpiderKingdom import models


from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class ProjectSerializer(serializers.ModelSerializer):
    domains = serializers.SerializerMethodField()
    class Meta:
        model = models.Project
        fields = '__all__'

    def get_domains(self,obj):
        queryset = obj.domain_set.all()
        return [ {'id':row.id,'name':row.domain}  for row in queryset]

class DomainSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name',read_only=True)
    cdn_name = serializers.CharField(source='cdn.cdn',read_only=True)
    status_description = serializers.CharField(source='status.status_description',read_only=True)
    class Meta:
        model = models.Domain
        fields = ['id','project','domain','cert_valid_date','cert_valid_days','check','warning','detection_interval',
                  'trigger','cdn','status','project_name','cdn_name','status_description','nodes']
        extra_kwargs = {}
        read_only_fields = []

class StatusCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StatusCode
        fields = '__all__'

class CDNSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CDN
        fields = '__all__'


class NodeSerializer(serializers.ModelSerializer):
    online_status = serializers.CharField(source='get_online_display',read_only=True)
    class Meta:
        model = models.Node
        fields = '__all__'

class FailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FailLog
        fields = '__all__'


class MonitorDataSerializer(serializers.ModelSerializer):
    node_name = serializers.CharField(source='node.node')
    class Meta:
        model = models.MonitorData
        fields = '__all__'

class SlaveGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Domain
        fields = ['id','domain','check','detection_interval']

class SlavePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MonitorData
        fields = ['http_code','total_time','datetime','node','domain','detection_interval']