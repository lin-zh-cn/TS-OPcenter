from datetime import datetime
from django.shortcuts import render, HttpResponse, redirect
from django.utils import datastructures
from django.http import JsonResponse,FileResponse
from django.http.request import QueryDict
from django.db.models import F

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.mixins import CreateModelMixin
# Create your views here.
from SaltStack.salt_manage import Key_manage,PlayBook_manage
key_manage = Key_manage()
playBook_manage = PlayBook_manage()
from SaltStack import models #import Groups, Minions, Playbooks, Playbooks_previous, Jobs
from SaltStack import rest_serializers #MinionsSerializer, GroupsSerializer
from SaltStack.tasks import minion_add, minion_test ,minion_grains, minion_state

class Paging(PageNumberPagination):
    """
    Minions列表分页信息
    """
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100

class GroupsViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取分组列表
    retrieve:
        获取分组详情
    """
    queryset = models.Groups.objects.all()
    serializer_class = rest_serializers.GroupsSerializer

class MinionsUnacceptedViewset(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = models.Minions.objects.all()
    serializer_class = rest_serializers.MinionsSerializer
    def list(self, request, *args, **kwargs):
        unaccepted_minion = key_manage.unaccepted_minion()
        print(unaccepted_minion)
        return Response(unaccepted_minion)

class MinionsFilter(django_filters.rest_framework.FilterSet):
    """
    主机过滤
    """
    status = django_filters.ChoiceFilter(field_name="status")
    group = django_filters.NumberFilter(field_name="group_id")
    minion_id = django_filters.CharFilter(field_name="minion_id",lookup_expr='icontains')
    ip = django_filters.CharFilter(field_name="ip", lookup_expr='icontains')

    class Meta:
        model = models.Minions
        fields = ['status', 'group', 'minion_id', 'ip']

class MinionsViewset(viewsets.ModelViewSet):
    """
    list:
        获取主机列表
    create:
        添加主机
    retrieve:
        获取一个主机信息
    update:
        更新一个主机信息
    patch:
        修改一个主机信息
    delete:
        删除一个主机
    """
    # SaltStack主机管理：列表页，分页，搜索，过滤，排序，添加，检测
    queryset = models.Minions.objects.all()
    serializer_class = rest_serializers.MinionsSerializer
    pagination_class = Paging
    filter_backends = (DjangoFilterBackend,)
    filter_class = MinionsFilter
    search_fields = ('status','group',)

    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        minion_id = request.data.get('minion_id')
        print(1111,request.data)
        if minion_add(minion_id):  # 添加salt-key成功
            # 写入基础信息
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            print(222)
            # 检测系统信息，使用队列
            grains_params = {'add':1, 'minion_id_list':[]}
            grains_params['minion_id_list'].append(minion_id)
            minion_grains.delay(grains_params)
            # 即时返回
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:  # 添加salt-key失败
            return JsonResponse({"code":9527,"msg":"salt执行错误"})

class Mnion_Test(mixins.CreateModelMixin,viewsets.GenericViewSet):
    queryset = models.Minions.objects.all()
    serializer_class = rest_serializers.MinionsSerializer
    pagination_class = Paging
    filter_backends = (DjangoFilterBackend,)
    filter_class = MinionsFilter
    search_fields = ('status','group',)
    def create(self, request, *args, **kwargs):
        id_list = request.data.get('id')
        minion_id_list = []
        for id in id_list:
            try:
                minion_id = models.Minions.objects.get(id=id).minion_id
                minion_id_list.append(minion_id)
            except Exception as err:
                return JsonResponse({"code":9527,"msg":id+','+str(err)})
        test_params = {'add':0, 'minion_id_list': minion_id_list}
        minion_test.delay(test_params)
        return JsonResponse({"code":0,"msg":"检测中"})

class Mnion_Grains(mixins.CreateModelMixin,viewsets.GenericViewSet):
    """
    http://192.168.2.250:8001/saltstack/api/minion_grains/
    Body:
        id = 1,2,3
    """
    queryset = models.Minions.objects.all()
    serializer_class = rest_serializers.MinionsSerializer
    pagination_class = Paging
    filter_backends = (DjangoFilterBackend,)
    filter_class = MinionsFilter
    search_fields = ('status','group',)
    def create(self, request, *args, **kwargs):
        print(request.data)
        id_list = request.data.get('id')
        minion_id_list = []
        for id in id_list:
            try:
                minion_id = models.Minions.objects.get(id=id).minion_id
                minion_id_list.append(minion_id)
                models.Minions.objects.filter(id=id).update(status=2)
            except Exception as err:
                return JsonResponse({"code":9527,"msg":id+','+str(err)})

        grains_params = {'add':0, 'minion_id_list': minion_id_list}
        print(grains_params)
        minion_grains.delay(grains_params)
        return JsonResponse({"code":0,"msg":"检测中"})

class PlaybooksFilter(django_filters.rest_framework.FilterSet):
    """
    剧本过滤
    """
    status = django_filters.BooleanFilter(field_name="status")
    group = django_filters.NumberFilter(field_name="group_id")
    class Meta:
        model = models.Playbooks
        fields = ['status','group',]

class PlaybooksViewset(viewsets.ModelViewSet):
    """
    get:
        获取剧本列表:list
        # http://192.168.2.250:8001/saltstack/api/playbook/?page=1
        获取一个历史版本详情:retrieve
        # http://192.168.2.250:8001/saltstack/api/playbook/1/
        过滤
        # http://192.168.2.250:8001/saltstack/api/playbook/?status=False
        # http://192.168.2.250:8001/saltstack/api/playbook/?group=2
    post:
        添加剧本:create
    patch:
        更新剧本:update
        # http://192.168.2.250:8001/saltstack/api/playbook/1/
        # body:data
    delete:
        删除一个剧本
    """
    queryset = models.Playbooks.objects.all()
    serializer_class = rest_serializers.PlaybooksSerializer
    pagination_class = Paging
    filter_backends = (DjangoFilterBackend,)
    filter_class = PlaybooksFilter
    search_fields = ('status','group',)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        print(1111111111111111111,'\n',data)
        data = playBook_manage.context_valid(data)
        print(2222222222222222222,type(data), '\n', data)
        if type(data) is dict or type(data) is QueryDict:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return JsonResponse({"code":9527,"msg":data})
    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        data = playBook_manage.context_valid(data)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if self.previous_update(kwargs.pop('pk'), request.data.get('change')):
            self.perform_update(serializer)
            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            return JsonResponse({"code":0,"msg":serializer.data})
        else:
            return JsonResponse({"code":9527,"msg":"修改失败"})

    def previous_update(self,id,change):
        try:
            playbook = models.Playbooks.objects.get(id=id)
            playbook_previous = models.Playbooks_previous.objects.filter(release_id=id).last()
            print(playbook)
            if playbook_previous is not None:
                if playbook.context == playbook_previous.context:
                    return False
            latest = {"release_id": id,
                      "change": change,
                      "description": playbook.description,
                      "context": playbook.context,
                      "lines": playbook.lines,
                      "update_time": playbook.update_time,
                      }
            print(latest)
            models.Playbooks_previous.objects.create(**latest)
            return True
        except Exception:
            return False

class PlaybooksPreviousViewset(viewsets.ModelViewSet):
    """
    list:
        获取当前剧本的历史版本列表
        http://192.168.2.250:8001/saltstack/api/playbook_previous/?id=13
    """
    queryset = models.Playbooks_previous.objects.all()
    serializer_class = rest_serializers.PlaybooksPreviousSerializer
    def list(self, request, *args, **kwargs):
        id = request.GET.get('id')
        previous_queryset = self.queryset.filter(release_id=id).values()
        return Response(previous_queryset)

class SelectMinionViewset(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = models.Minions.objects.all()
    serializer_class = rest_serializers.SelectMinionsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = MinionsFilter
    search_fields = ('group',)
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class SelectPlaybookViewset(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = models.Playbooks.objects.filter(status=True)
    serializer_class = rest_serializers.SelectPlaybookSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = PlaybooksFilter
    search_fields = ('group',)
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class JobsFilter(django_filters.rest_framework.FilterSet):
    """
    主机过滤
    """
    nobefore = django_filters.DateTimeFilter(field_name="create_time",help_text="时间筛选起点",lookup_expr='gte')
    noafter = django_filters.DateTimeFilter(field_name="create_time", help_text="时间筛选终点", lookup_expr='lte')
    group = django_filters.NumberFilter(field_name="group_id")
    minion_id = django_filters.CharFilter(field_name="minions",lookup_expr='iexact')
    class Meta:
        model = models.Jobs
        fields = ['nobefore', 'noafter', 'group', 'minion_id']

class JobsViewset(mixins.ListModelMixin,mixins.CreateModelMixin,viewsets.GenericViewSet):
    queryset = models.Jobs.objects.all()
    serializer_class = rest_serializers.JobsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = JobsFilter
    search_fields = ('nobefore', 'noafter', 'group', 'minion_id',)

    def create(self, request, *args, **kwargs):
        print(request.data)
        # 生成任务编号number=yyyymmdd+000
        job_last = models.Jobs.objects.last()
        today = datetime.today().strftime('%Y%m%d')
        try:
            number = str(int(job_last.number)+1) if job_last.number[0:8] == today else today+'001'
        except AttributeError:
            number = today+'001'
        # 获取剧本和所属分组
        playbook_id = request.data.get('description')
        group_id = models.Playbooks.objects.get(id=playbook_id).group_id
        # 获取主机列表
        minion_list = request.data.get('minions')
        # 保存任务基础信息
        jobs_base = models.Jobs(number=number, targets_total=len(minion_list), description_id=playbook_id, group_id=group_id)
        jobs_base.save()
        # 保存多对多受影响主机
        try:
            jobs_base.minions.add(*minion_list)
        except Exception as error:
            print(error)
        # 获取主机salt_minion_id
        minions_obj = models.Minions.objects.in_bulk(minion_list)
        minion_id_list = []
        for id in minions_obj:
            minion_id_list.append(str(minions_obj.get(id)))
            # 更新主机任务计数
            models.Minions.objects.filter(id=id).update(jobs_count=F('jobs_count') + 1)
        # 使用队列，异步执行salt.state.sls
        state_params = {"number":number, "minion_id_list":minion_id_list, "playbook_id":playbook_id}
        minion_state.delay(state_params)

        return JsonResponse({"code":0,"msg":"任务已加入队列"})


