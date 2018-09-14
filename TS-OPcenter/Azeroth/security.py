from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from .models import UserToken
from .apiexception import NotLogin
from SpiderKingdom.models import Node


class AuthLogin(BaseAuthentication):
    def authenticate(self, request):
        print(request.session.items())
        user_id = request.session.get('_auth_user_id')
        if user_id is None:
            raise NotLogin()


class AuthToken(BaseAuthentication):
    def authenticate(self,request):
        token = request.GET.get('token')
        user_id = request.session.get('_auth_user_id')
        token_obj = UserToken.objects.filter(user_id=user_id).first()
        if token_obj:
            if token_obj.token == token:
                return token_obj.user.username, token_obj.token
            else:
                raise exceptions.AuthenticationFailed("身份验证失败!")
        else:
            raise exceptions.AuthenticationFailed("身份验证失败!")

class AuthSlave(BaseAuthentication):
    def authenticate(self, request):
        slave_ip = request.META['REMOTE_ADDR']
        node_obj = Node.objects.filter(ip=slave_ip).first()
        if node_obj is None:
            raise exceptions.AuthenticationFailed("身份验证失败!")
        return node_obj.id, node_obj.ip



class AuthPermission(BaseAuthentication):
    def has_permission(self,request,view):
        if 1:
            return True

