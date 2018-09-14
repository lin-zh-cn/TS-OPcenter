import json
import hashlib, time

from django.shortcuts import render
from django.shortcuts import HttpResponse
from rest_framework.response import Response
from django.contrib import auth
from rest_framework import status

from .models import UserToken
# Create your views here.

def get_random_str(user):

    ctime=str(time.time())

    md5=hashlib.md5(bytes(user,encoding="utf8"))
    md5.update(bytes(ctime+'**',encoding="utf8"))

    return md5.hexdigest()


def login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        user = auth.authenticate(username=data['username'],password=data['password'])
        if user is not None:
            auth.login(request,user)
            random_str = get_random_str(data['username'])
            token = UserToken.objects.update_or_create(user=user,defaults={'token':random_str})
            data = {
                'status_code':status.HTTP_200_OK,
                'token':random_str
            }
            return HttpResponse(json.dumps(data))
        else:
            data = {
                'status_code': status.HTTP_401_UNAUTHORIZED,
            }
            return HttpResponse(json.dumps(data))