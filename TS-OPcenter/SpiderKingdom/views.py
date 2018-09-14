import time
import datetime
import json
# Create your views here.
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.viewsets import mixins
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.db.models import Q,Count

from django.contrib.auth.models import User, Group
from SpiderKingdom import rest_serializers
from SpiderKingdom import models
from StormwindCity.tasks import cert_check
from Azeroth.security import AuthSlave
from SpiderKingdom import tasks

# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = rest_serializers.UserSerializer
#
#
# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = rest_serializers.GroupSerializer


class DomainListPageNumberPagination(PageNumberPagination):
    """
    域名管理的分页
    """
    page_query_param = "page"
    page_size = 10


class DomainFilter(django_filters.rest_framework.FilterSet):
    """
    DomainViewSet过滤类
    """
    check = django_filters.BooleanFilter(field_name='check')
    warning = django_filters.BooleanFilter(field_name='warning')
    status = django_filters.CharFilter(field_name='status')
    project = django_filters.CharFilter(field_name='project')
    cert_day = django_filters.NumberFilter(field_name='cert_valid_days', lookup_expr='lte')
    domain = django_filters.CharFilter(field_name='domain',lookup_expr='icontains')
    domain_exact = django_filters.CharFilter(field_name='domain',lookup_expr='exact')

    class Meta:
        model = models.Domain
        fields = ['check','warning','domain','status','project','cert_day','domain_exact']


class DomainViewSet(viewsets.ModelViewSet):
    """
    list:
        获取域名信息
    create:
        新建一个域名
    retrieve:
        获取单个域名信息
    update:
        更新一条域名信息
    patch:
        修改域名信息
    delete:
        删除一条域名信息
    """
    queryset = models.Domain.objects.all()
    serializer_class = rest_serializers.DomainSerializer
    pagination_class = DomainListPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = DomainFilter
    search_fields = ('check','warning','domain','status','project','cert_day','domain_exact')

    # 域名管理的列表
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)

        not_check = models.Domain.objects.filter(check=False).count()
        not_warning = models.Domain.objects.filter(warning=False).count()
        cert_expire = models.Domain.objects.filter(cert_valid_days__lte=10).count()
        fault_domain = models.Domain.objects.filter(~Q(status=1)).count()
        projects = models.Project.objects.all().values('id','name')
        # print(self.get_paginated_response())
        data = {
            'status_code':0,
            'not_check':not_check,
            'not_warning':not_warning,
            'cert_expire':cert_expire,
            'fault_domain':fault_domain,
            'data': serializer.data,
            'projects':projects
        }
        return self.get_paginated_response(data)

    # 新增一条域名数据
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({"status_code":0,'data':serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
        else:
            headers = self.get_success_headers(serializer.data)
            return Response({"status_code":9527,"data":serializer.errors}, headers=headers)


class SlaveGetViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    list:
        Slave获取数据接口
    """
    authentication_classes = [AuthSlave,]
    permission_classes = []

    queryset = models.Domain.objects.all()
    serializer_class = rest_serializers.SlaveGetSerializer

    # Slave获取数据
    def list(self, request, *args, **kwargs):
        queryset_in_node = self.queryset.filter(nodes=request.user)
        models.Node.objects.filter(id=request.user).update(last_active=datetime.datetime.now())
        serializer = self.get_serializer(queryset_in_node, many=True)
        data = {
            'node':request.user,
            'data':serializer.data
        }
        return Response(data)


class SlavePostObj(object):
    """
    Slave的数据对象类
    """
    def __init__(self,result):
        self.fail_num = 0                                                                   # 满足失败个数的次数
        self.update_time = time.mktime(time.strptime(result['datetime'],"%Y-%m-%d %H:%M:%S"))    # 本次采集时间
        self.clean = []                                                                     # 本次采集失败的节点
        self.domain = models.Domain.objects.get(id=result['domain'])                        # 域名对象
        self.stain = []

    # 清空上一时间段检测正常和失败的记录
    def update(self,datetime):
        self.stain = []
        self.clean = []
        self.update_time = time.mktime(time.strptime(datetime, "%Y-%m-%d %H:%M:%S"))


class SlavePostCleaning(object):
    """
    缓存上一次的检测记录，用于判断是否触发邮件警告
    """
    def __init__(self):
        self.bathhouse = {}
        self.slavepostobj = SlavePostObj

    # 主要的判断方法，并将检测异常的数据存入FailLog表
    def add(self,result):
        if result['domain'] not in self.bathhouse:
            self.bathhouse[result['domain']] = self.slavepostobj(result)

        slavePostObj = self.bathhouse[result['domain']]
        if time.time() - slavePostObj.update_time >= int(result['detection_interval']):
            print(slavePostObj.clean, slavePostObj.stain)
            if not len(slavePostObj.clean) <= int(slavePostObj.domain.nodes.count()) / 2:
                slavePostObj.fail_num += 1
                slavePostObj.update(result['datetime'])
                if slavePostObj.fail_num >= slavePostObj.domain.trigger:
                    print("发送邮件 {}".format(slavePostObj.domain.domain))
                    self.sendmail(slavePostObj)
                    slavePostObj.fail_num = 0
                    return
                return
            slavePostObj.fail_num = 0
            slavePostObj.update(result['datetime'])

        if 'total_time' not in result:
            slavePostObj.clean.append(result['node'])
        else:
            slavePostObj.stain.append(result['node'])
            models.FailLog.objects.create(domain_id=result['domain'],
                                          node_id=result['node'],
                                          datetime=result['datetime'])



    # 调用celery发送邮件任务发送邮件
    def sendmail(self,slavePostObj):
        content = '域名:{}<br>CDN:{}<br>项目:{}<br>故障节点:'.format(slavePostObj.domain.domain,
                                                        None if slavePostObj.domain.cdn is None else slavePostObj.domain.cdn.cdn,
                                                        None if slavePostObj.domain.project is None else slavePostObj.domain.project.name)
        for node_id,node_obj in models.Node.objects.in_bulk(slavePostObj.stain).items():
            content + '{}  '.format(node_obj.node)
        tasks.send_mail.delay(slavePostObj.domain.domain,content)
        return True



class SlavePostViewSet(mixins.CreateModelMixin,viewsets.GenericViewSet):
    """
    create:
        Slave提交数据接口
    """

    authentication_classes = [AuthSlave, ]
    permission_classes = []

    queryset = models.MonitorData.objects.all()
    serializer_class = rest_serializers.SlavePostSerializer

    Cleaner = SlavePostCleaning()

    # 将数据存入MonitorData表，并将数据放入SlavePostCleaning实例中清洗，判断是否触发邮件警告，并将检测异常的数据存入FailLog表
    def create(self, request, *args, **kwargs):
        self.Cleaner.add(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



class MonitorDataList(mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    域名状态分析的图标数据
    """
    queryset = models.MonitorData.objects.all()
    serializer_class = rest_serializers.MonitorDataSerializer

    #
    def list(self, request, *args, **kwargs):
        last_time = settings.SPIDERKINGDOM_CHART_LAST
        current_time = time.time()
        start_time_s = time.localtime(current_time - last_time)
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", start_time_s)
        domain_obj = models.Domain.objects.get(id=kwargs.get("domain_id"))
        chart_queryset = self.queryset.filter(datetime__gte=start_time).filter(**kwargs)

        chart_data = []

        for node in domain_obj.nodes.all():
            single_node = chart_queryset.filter(node_id=node.id)

            serializer = self.get_serializer(single_node, many=True)
            node_data = {
                "node_name":node.node,
                "project": None if domain_obj.project is None else domain_obj.project.name,
                "cdn": None if domain_obj.cdn is None else domain_obj.cdn.cdn,
                "status": domain_obj.status.status_description,
                "data":serializer.data
            }

            chart_data.append(node_data)
        return Response(chart_data)


class ProjectViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    list:
        获取所有项目信息
    """
    queryset = models.Project.objects.all()
    serializer_class = rest_serializers.ProjectSerializer




class CDNViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    list:
        获取所有CDN信息
    """
    queryset = models.CDN.objects.all()
    serializer_class = rest_serializers.CDNSerializer





class NodeViewSet(viewsets.ModelViewSet):
    """
    list:
        获取所有节点信息
    """
    queryset = models.Node.objects.all()
    serializer_class = rest_serializers.NodeSerializer



    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)





class FailLogListPageNumberPagination(PageNumberPagination):
    """
    域名检测失败日志的分页
    """
    page_query_param = "page"
    page_size = 10

class FailLogViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):

    queryset = models.FailLog.objects.all()
    serializer_class = rest_serializers.FailLogSerializer
    pagination_class = FailLogListPageNumberPagination



class CertViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    检测证书
    """
    queryset = models.Domain.objects.all()
    serializer_class = rest_serializers.DomainSerializer

    # 调用celery的检测证书任务检测证书到期时间
    def list(self, request, *args, **kwargs):
        data = request.GET.get('domain')
        cert_check.delay(data)
        return Response({'status_code':0,"data":"任务提交成功"})




class Domain_To_NodeSet(mixins.UpdateModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):
        """
        节点管理的穿梭框里的数据
        """
        node_id = kwargs.get("node_id")
        node_obj = models.Node.objects.get(id=node_id)
        in_node = node_obj.domain_set.all().values('id','domain')
        outside_node = models.Domain.objects.exclude(nodes=node_obj.id).values()

        # 不属于本节点的数据列表
        outside_node_data = []

        # 属于本节点的数据列表
        in_node_data = []

        for project in models.Project.objects.all():
            outside_project_menu = {
                'id':project.id,
                'label':project.name,
                'pid':0,
                'children': [ {'id':i['id'],'label':i['domain'],'pid':1} for i in outside_node.filter(project=project).values('id', 'domain')]
            }
            outside_node_data.append(outside_project_menu)

            in_project_menu = {
                'id':project.id,
                'label': project.name,
                'pid': 0,
                'children': [ {'id':i['id'],'label':i['domain'],'pid':1} for i in in_node.filter(project=project).values('id', 'domain')]
            }
            in_node_data.append(in_project_menu)

        data = {
            'in_node':in_node_data,
            'outside_node': outside_node_data
        }
        return Response(data)

    def update(self, request, *args, **kwargs):
        try:
            node_id = kwargs.get("node_id")
            node_obj = models.Node.objects.get(id=node_id)
            print(request.data)
            node_obj.domain_set.set(request.data)
            return Response(request.data)
        except Exception as e:
            return Response({'status_code':9527,"data":"更新出错"})