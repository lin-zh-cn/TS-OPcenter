from __future__ import absolute_import, unicode_literals
import datetime,time
from celery import shared_task
from celery.task import task
from SaltStack.models import Minions
from SaltStack.salt_manage import Grains_item, Test_ping, Key_manage, State_sls


@task(queue="minion_state",routing_key='minion_state')
def minion_state(state_params):
    print("接收任务",state_params)
    obj = State_sls(state_params)
    obj.exe_sls()
    return "执行完成"

@shared_task
def minion_add(minion_id):
    try:
        obj = Key_manage()
        obj.accept_key(minion_id=minion_id)
        print("添加成功"+minion_id)
        return True
    except Exception:
        return False

@shared_task
def minion_grains(grains_params):
    if grains_params['minion_id_list']:
        # 如果是新添加，则延迟检测
        time.sleep(30) if grains_params['add'] == 1 else None
        # 检测主机信息
        obj = Grains_item()
        obj.get_minion_items(grains_params['minion_id_list'])
        return True
    else:
        return None

@shared_task
def minion_test(test_params):
    # id不能为空，避免异常
    if test_params['minion_id_list']:
        # 如果是新添加，则延迟检测
        time.sleep(15) if test_params['add'] == 1 else None
        # 检测主机信息
        obj = Test_ping()
        obj.get_status(test_params['minion_id_list'])
        return True
    else:
        return None