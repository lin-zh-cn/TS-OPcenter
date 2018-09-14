from __future__ import absolute_import, unicode_literals
import random

from celery import shared_task

from SpiderKingdom.models import Domain

from StormwindCity.Cert_Check_Module import PySSL_Check
from StormwindCity.Cert_Check_Module import Myssl_Check
from StormwindCity.Cert_Check_Module import SSLceshi_Check



@shared_task
def cert_check(domain):
    other = [Myssl_Check, SSLceshi_Check]
    obj = PySSL_Check(domain)
    obj.requests()
    data = obj.ret_valid()

    verifyState = data.pop('verifyState')
    if verifyState != 0:
        for i in range(0,len(other)):
            check_obj = other.pop(random.randrange(0,len(other)))
            obj = check_obj(domain)
            obj.requests()
            data = obj.ret_valid()
            verifyState = data.pop('verifyState')
            print(2,data)
            if verifyState == 0:
                break
    Domain.objects.filter(domain=domain).update(**data)
    return "执行完成"
