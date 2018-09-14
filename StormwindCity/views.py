import os
import json
# Create your views here.
from django.http import JsonResponse,FileResponse


from StormwindCity.FreeSSL  import TrustAsia
from StormwindCity.Cert_Check_Module import Myssl_Check
from StormwindCity.Cert_Check_Module import SSLceshi_Check




# ---------------------------------------------TrustAsia证书管理---------------------------------------------------------


def TrustAsia_apply(request):
    """
    TrustAsia证书申请页面
    :param request:
    :return:
    """

    if request.method == "GET":
        TrustAsia_obj = TrustAsia()
        # result = TrustAsia_obj.login()
        return JsonResponse({"code":0,"msg":"登陆成功"})
        # return Response(result)
    else:
        return JsonResponse({"code":9527,"msg":"拒绝访问"})

# class TrustAsia_apply(viewsets.ModelViewSet):
#     """
#     list:
#         登陆到FreeSSL
#     """
#     queryset = []
#     def list(self, request, *args, **kwargs):
#             TrustAsia_obj = TrustAsia()
#             # result = TrustAsia_obj.login()
#             return Response({"code":0,"msg":"登陆成功"})
#             # return Response(result)


def TrustAsia_apply_create_order(request):

    """
    TrustAsia创建订单
    :param request:
    :return:
    """
    if request.method == "POST":
        domain = json.loads(request.body.decode())['domain']
        algorithm = json.loads(request.body.decode())['algorithm']
        TrustAsia_obj = TrustAsia()
        result = TrustAsia_obj.Create_order(domain,algorithm)
        # response = {'msg': {'order_id': 'Dehz1wHa19bc3', 'auth_info': [{'auth_key': 'test52.linlim.cn', 'auth_value': '201806140731241a08yxu60kcc1x4lip25fnvtkzos5xag85ch85pncy2jrv449p', 'auth_path': '_dnsauth.test52'}]}, 'code': 0}
        return JsonResponse(result)
    else:
        return JsonResponse({"code":9527,"msg":"拒绝访问"})

# class TrustAsia_apply_create_order(mixins.CreateModelMixin,viewsets.GenericViewSet):
#     def create(self, request, *args, **kwargs):
#         # domain = json.loads(request.body.decode())['domain']
#         domain = request.data['domain']
#         # algorithm = json.loads(request.body.decode())['algorithm']
#         algorithm = request.data['algorithm']
#         TrustAsia_obj = TrustAsia()
#         result = TrustAsia_obj.Create_order(domain,algorithm)
#         # response = {'msg': {'order_id': 'Dehz1wHa19bc3', 'auth_info': [{'auth_key': 'test52.linlim.cn', 'auth_value': '201806140731241a08yxu60kcc1x4lip25fnvtkzos5xag85ch85pncy2jrv449p', 'auth_path': '_dnsauth.test52'}]}, 'code': 0}
#         return Response(result)
#
#     def get_serializer(self, *args, **kwargs):
#         return


def TrustAsia_apply_Order_Authz(request):
    """
    TrustAsia验证订单
    :param request:
    :return:
    """
    if request.method == "POST":
        order_id = json.loads(request.body.decode())['order_id']
        domain = json.loads(request.body.decode())['domain']
        TrustAsia_obj = TrustAsia()
        result = TrustAsia_obj.Order_Authz(domain,order_id)
        return JsonResponse(result)
    else:
        return JsonResponse({"code":9527,"msg":"拒绝访问"})

# class TrustAsia_apply_Order_Authz(mixins.CreateModelMixin,viewsets.GenericViewSet):
#     def create(self, request, *args, **kwargs):
#         domain = request.data['domain']
#         order_id = request.data['order_id']
#         TrustAsia_obj = TrustAsia()
#         result = TrustAsia_obj.Order_Authz(domain, order_id)
#         return Response(result)
#
#     def get_serializer(self, *args, **kwargs):
#         return




def TrustAsia_download_nginx(request,domain):
    """
    TrustAsia下载nginx证书包
    :param request:
    :param domain:
    :return:
    """
    if request.method == "GET":
        TrustAsia_obj = TrustAsia()
        file_abspath = TrustAsia_obj.Cert_nginx_download(domain)
        print(domain)
        filename = os.path.basename(file_abspath)
        if os.path.exists(file_abspath):
            file_download = open(file_abspath, 'rb')
            response = FileResponse(file_download)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename=%s' % filename
            return response
        else:
            return JsonResponse({"status_code":404,"message":"文件不存在"})
    else:
        return JsonResponse({"code":9527,"msg":"拒绝访问"})



def TrustAsia_download_iis(request,domain):
    """
    TrustAsia下载iis证书包
    :param request:
    :param domain:
    :return:
    """
    if request.method == "GET":
        TrustAsia_obj = TrustAsia()
        file_abspath = TrustAsia_obj.Cert_iis_download(domain)
        filename = os.path.basename(file_abspath)
        if os.path.exists(file_abspath):
            file_download = open(file_abspath, 'rb')
            response = FileResponse(file_download)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename=%s' % filename
            return response
        else:
            return JsonResponse({"status_code": 404, "message": "文件不存在"})

def TrustAsia_order_list(request):
    """
    TrustAsia订单列表
    :param request:
    :param page:
    :return:
    """
    if request.method == "GET":
        TrustAsia_obj = TrustAsia()
        orderList = TrustAsia_obj.Order_list()
        return JsonResponse(orderList)
    else:
        return JsonResponse({"code":9527,"msg":"拒绝访问"})

def TrustAsia_cert_list(request):
    """
    TrustAsia证书列表
    :param request:
    :return:
    """
    if request.method == "GET":
        TrustAsia_obj = TrustAsia()
        certList = TrustAsia_obj.Cert_list()
        return JsonResponse(certList)
    else:
        return JsonResponse({"code":9527,"msg":"拒绝访问"})


def TrustAsia_order_detail(request):
    """
    TrustAsia订单详情
    :param request:
    :param order_id:
    :return:
    """
    if request.method == "POST":
        TrustAsia_obj = TrustAsia()
        order_id = json.loads(request.body.decode())['order_id']
        print(order_id)
        orderDetail = TrustAsia_obj.Orders_detail(order_id)
        return JsonResponse(orderDetail)
    else:
        return JsonResponse({"code":9527,"msg":"拒绝访问"})

def TrustAsia_order_delete(request):
    """
    TrustAsia删除订单
    :param request:
    :return:
    """
    if request.method == "POST":
        TrustAsia_obj = TrustAsia()
        order_id = json.loads(request.body.decode())['order_id']
        status = json.loads(request.body.decode())["status"]
        result = TrustAsia_obj.Order_delete(order_id,status)
        return JsonResponse(result)
    else:
        return JsonResponse({"code":9527,"msg":"拒绝访问"})

def TrustAsia_cert_detail(request):
    if request.method == "POST":
        sha1 = json.loads(request.body.decode())['sha1']
        TrustAsia_obj = TrustAsia()
        cert_detail = TrustAsia_obj.Cert_detail(sha1)
        return JsonResponse(cert_detail)
    else:
        return JsonResponse({"code":9527,"msg":"拒绝访问"})

def TrustAsia_cert_delete(request):
    if request.method == "POST":
        sha1 = json.loads(request.body.decode())['sha1']
        TrustAsia_obj = TrustAsia()
        result = TrustAsia_obj.Cert_delete(sha1)
        # return HttpResponse(json.dumps(result))
        return JsonResponse(result)

def TrustAsia_cert_select(request):
    if request.method == "POST":
        order_id = json.loads(request.body.decode())['order_id']
        TrustAsia_obj = TrustAsia()
        result = TrustAsia_obj.Cert_select(order_id)
        return JsonResponse(result)
    else:
        return JsonResponse({"code":9527,"msg":"拒绝访问"})



def myssl_check(request):
    if request.method == 'GET':
        domain = request.GET.get('domain')
        obj = Myssl_Check(domain)
        obj.requests()
        data = obj.ret_response()
        return JsonResponse(data)
    else:
        return JsonResponse({"code": 9527, "msg": "拒绝访问"})

def sslceshi_check(request):
    if request.method == 'GET':
        domain = request.GET.get('domain')
        obj = SSLceshi_Check(domain)
        obj.requests()
        data = obj.ret_response()
        return JsonResponse(data)
    else:
        return JsonResponse({"code":9527,"msg":"拒绝访问"})


