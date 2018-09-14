import time,datetime,os,shutil,json
from django.http import JsonResponse
from django.core.files import uploadedfile
from salt import client,config,key
from SaltStack.models import Minions,Playbooks,Groups,Jobs
from SaltStack.job_ret_parse import PlaybookResponse
from TS.settings import BASE_DIR
EXCEPT_DATA = {'status_code' : 9527}
SUCCESS_DATA = {'status_code' : 0 }
# 管理key
class Key_manage(object):
    def __init__(self):
        self.opts = config.master_config('/etc/salt/master')
        self.key = key.get_key(self.opts)
        self.all_keys = self.key.list_keys()
    # key列出----------------------------------
    # 列出全部minion的key
    def all_keys(self):
        return self.all_keys
    # 已添加的minion
    def accepted_minion(self):
        return self.all_keys['minions']
    # 待添加的minion
    def unaccepted_minion(self):
        return self.all_keys['minions_pre']
    # 已经拒绝的minion
    def rejected_minion(self):
        return self.all_keys['minions_rejected']
    # key操作---------------------------------
    # 添加minion
    def accept_key(self,minion_id):
        try:
            self.key.accept(minion_id)
            return True
        except Exception as err:
            return err
    # 拒绝minion的key
    def reject_key(self,minion_id):
        try:
            self.key.reject(minion_id)
            return True
        except Exception as err:
            return err
    # 删除minion的key
    def delete_key(self,minion_id):
        try:
            self.key.delete_key(minion_id)
            return True
        except Exception as err:
            return err
# Grains模块----------------
class Grains_item(client.LocalClient):
    # 获取节点系统和硬件配置，minion_id_list是一个列表
    def get_minion_items(self,minion_id_list):
        # 定义需要获取的信息
        items = ['osfinger', 'cpu_model', 'num_cpus', 'mem_total']
        result = self.cmd(minion_id_list, 'grains.item', items,tgt_type='list')
        self.save_minion_items(minion_id_list,result)
    # grains结果解析及保存
    def save_minion_items(self,minion_id_list,result):
        # 写入数据库，判断检测是否有结果
        data = {}
        if len(result) != 0:
            for minion_id in result.keys():
                minion_item = result[minion_id]
                # 判断检测结果是否成功
                if type(minion_item) is dict:
                    minion_item['last_test'] = datetime.datetime.now()
                    minion_item['last_online'] = datetime.datetime.now()
                    mem_gib = 0.5 if round((minion_item['mem_total']) / 1024) == 0 else round(
                        (minion_item['mem_total']) / 1024)
                    minion_item['mem_gib'] = mem_gib
                    minion_item['status'] = 1
                    Minions.objects.filter(minion_id=minion_id).update(**minion_item)
                    data[minion_id] = "成功；"
                else:
                    errinfo = {'last_test': datetime.datetime.now(),
                               'cpu_model': '主机不在线',
                               'osfinger': '主机不在线',
                               'mem_gib': 0,
                               'mem_total': 0,
                               'num_cpus': 0,
                               'status': 0,
                               }
                    Minions.objects.filter(minion_id=minion_id).update(**errinfo)
                    data[minion_id] = "不在线；"
        else:
            for minion_id in minion_id_list:
                errinfo = {'last_test': datetime.datetime.now(),
                           'cpu_model': '不存在的KEY',
                           'osfinger': '不存在的KEY',
                           'mem_gib': 0,
                           'mem_total': 0,
                           'num_cpus': 0,
                           'status': 3,
                           }
                Minions.objects.filter(minion_id=minion_id).update(**errinfo)
                data[minion_id] = "不存在；"
        return {"主机配置检测完成": data}
# Test模块
class Test_ping(client.LocalClient):
    # 获取主机的状态
    def get_status(self,minion_id_list):
        # 接收test.ping的返回结果
        result = self.cmd(minion_id_list,'test.ping',[],tgt_type='list')
        #result必然是一个字典
        self.save_status(result)
    def save_status(self,result):
        # result必然是一个字典
        # 更新数据库
        for minion_id in result.keys():
            if result[minion_id]:  # True=1；False=0
            # 检测状态更新到数据库
                data = {"status":True,
                        "last_test":datetime.datetime.now(),
                        "last_online":datetime.datetime.now(),
                        }
            else:
                data = {"status":False,
                        "last_test":datetime.datetime.now(),
                        }
            Minions.objects.filter(minion_id=minion_id).update(**data)
        return {"联机状态检测完成":result}
# 剧本管理
class PlayBook_manage():
    def __init__(self):
        # 配置文件导入目录 sls_conf
        self.init_conf = '%s/saltstack/init_conf/' % BASE_DIR
        self.state_sls = '%s/saltstack/state_sls/' % BASE_DIR
        self.salt_etc = '/etc/salt/'
        self.srv_salt = '/srv/salt/'

    def context_valid(self,data):

        # 上传剧本文件
        if data.get('file') is None or data.get('file') == '':
            return "File或Context不能为空"

        if type(data['file']) is uploadedfile.InMemoryUploadedFile:
            try:
                context = data['file'].chunks().__next__().decode()
            except Exception as error:
                return "%s：必须是utf-8编码(%s)" % (str(data['file']), str(error)[0:70])
        # 在线编辑内容添加
        else:
            context = data['file']
        # 获得剧本描述
        try:
            description = context.splitlines()[1][2:]
        except IndexError:
            return "内容不规范"
        # 获得剧本所在分组ID
        try:
            group = context.splitlines()[0][2:]
            group_id = Groups.objects.get(name=group).id
        except Exception:
            return "分组不存在"
        # 获得剧本行数
        lines = context.count('\n') + 1
        # 更新data
        data.update({"context":context, "lines":lines, "description":description, "group":group_id, "update_time":datetime.datetime.now(), "status":True, "file":None})
        return data

    # 查看和编辑
    def save(self, playbook_path,playbook_context):
        try:
            with open(playbook_path, 'w') as f:
                f.write(playbook_context)
            return True
        except Exception as error:
            return error

    def delete(self,playbook_path):
        try:
            # 删除文件（移动到回收目录）
            playbook_file = os.path.basename(playbook_path)
            recycling = '/srv/salt/Recycling/'
            os.makedirs(recycling) if not os.path.exists(recycling) else None
            shutil.move(playbook_path,recycling+playbook_file)
            # 删除数据库记录
            Playbooks.objects.filter(applied_file=playbook_path).delete()
            return True
        except Exception as error:
            return error
# 执行剧本
class State_sls(object):
    def __init__(self,state_params):
        # 开始执行，更新status=1，start_time=now
        self.number = state_params['number']
        Jobs.objects.filter(number=self.number).update(status=1, start_time=datetime.datetime.now())
        playbook_obj = Playbooks.objects.get(id=state_params['playbook_id'])
        base_path = '/srv/salt/%s.sls'%playbook_obj.description
        with open(base_path,'w') as f:
            f.write(playbook_obj.context)
        self.minions = state_params['minion_id_list']
        self.sls = playbook_obj.description
        self.client = client.LocalClient()
    # 执行剧本
    # def exe_sls(self,number,minion_id_list, playbook_id):
    def exe_sls(self):
        # result = self.client.cmd_async(state_params['minion_id_list'], 'state.sls', [self.sls],tgt_type='list')
        try:
            response = self.client.cmd(self.minions, 'state.sls', [self.sls], tgt_type='list')
            # 更新jid到数据库
            self.save_sls(response)
        except Exception as error:
            print(error)
            Jobs.objects.filter(number=self.number).update(finish_time=datetime.datetime.now(), status=3, information={'ERROR':str(error)})
        # 失败 {'md_linux_op_node142_local_vmm': False}

    # 保存执行结果
    def save_sls(self,response):
        format_info = PlaybookResponse(response)
        print(format_info)
        try:
            Jobs.objects.filter(number=self.number).update(finish_time=datetime.datetime.now(), status=2, information=format_info.all, success_total=format_info.all['success'])
        except Exception:
            Jobs.objects.filter(number=self.number).update(finish_time=datetime.datetime.now(), status=2, information=format_info.all, success_total=0)
        # if 'ERROR' in information:
        #     Jobs.objects.filter(number=number).update(finish_time=finish_time, status=3,success_total=0,information=json.dumps(information))
        # else:
        #     format_info = PlaybookResponse(information)
        #     try:
        #         Jobs.objects.filter(number=number).update(finish_time=finish_time, status=2, success_total=format_info.all['success'],information=format_info.all)
        #     except Exception:
        #         Jobs.objects.filter(number=number).update(finish_time=finish_time, status=2, success_total=0, information=format_info.all)


# master配置
# class Master_manage():
#     def __init__(self):
#         # 配置文件导入目录 sls_conf
#         self.init_conf = '%s/saltstack/init_conf/' % BASE_DIR
#         self.state_sls = '%s/saltstack/state_sls/' % BASE_DIR
#         self.salt_etc = '/etc/salt/'
#         self.srv_salt = '/srv/salt/'
#     # master配置初始化
#     def master_init(self):
#         # 判断salt安装与否
#         if os.path.exists(self.salt_etc):
#
#             # Grains自定义目录
#             grains_path = self.srv_salt+'_grains/'
#             os.makedirs(grains_path) if not os.path.exists(grains_path) else 'grains path existed'
#             # 初始化目录
#             init = self.srv_salt+'init'
#             os.makedirs(init) if not os.path.exists(init) else 'init path existed'
#             # 备份master配置文件
#             if os.path.exists(self.salt_etc+'master'):
#                 master_bak = 'master_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
#                 os.rename(self.salt_etc+'master', self.salt_etc+'master_bak')
#             # 删除90天前的master_前缀的配置文件备份
#             for master_bak in os.listdir(self.salt_etc):
#                 if master_bak.startswith('master_') and time.time() - os.path.getmtime(self.salt_etc+'master_bak') > 90*24*3600:
#                     os.remove(master_bak)
#             # 导入master的配置文件
#             shutil.copyfile(self.init_conf + 'master', self.salt_etc+'master')
#             return True
#         else:
#             return False
#
#     def grains_defined(self):
#         # 导入自定义grains文件
#         grains_path = '/srv/salt/_grains/'
#         grains_file = '/srv/salt/_grains/grains_defined.py'
#         if os.path.exists(grains_file):
#             grains_bak = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '_grains'
#             os.rename(grains_file, grains_path + grains_bak)
#         shutil.copyfile(self.init_conf + 'grains_defined.py', '/srv/salt/_grains/grains_defined.py')
#
#         result = client.LocalClient().cmd_async('*', 'saltutil.sync_all', [])
#         #result = client.LocalClient().cmd(minion_id, 'grains.item', ['md_op_linux_beijing_opcenter-slave','md_op_linux_shanghai_opcenter-slave','md_op_linux_qingdao_opcenter-slave','md_op_linux_shenzhen_opcenter-slave'])
#         return result




