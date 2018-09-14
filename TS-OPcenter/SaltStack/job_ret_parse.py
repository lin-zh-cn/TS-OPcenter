import re
from math import ceil

class PlaybookEvent(object):
    def __init__(self,k,event):
        self.event_name = None
        self.event_target = None
        self.module = None
        self.num = None
        self.duration = None
        self.sls = None
        self.comment = None
        self.result = None
        self.start_time = None
        self.changes = None
        self.parse(k,event)

    def parse(self,k,event):
        self.module = self.parse_module(k)
        self.event_name = event.get('__id__')
        self.event_target = event.get('name')
        self.num = event.get('__run_num__')
        self.duration = ceil(event.get('duration'))/1000
        self.sls = event.get('__sls__')
        self.comment = event.get('comment')
        self.result = event.get('result')
        self.start_time = event.get('start_time')
        self.changes = event.get('changes')

    def parse_module(self,k):
        m = re.search(r'(.*?)_',k).group(1)
        f = re.search(r'.*\|(.*?$)',k).group(1)
        return m+f

    def todict(self):
        return self.__dict__

class PlaybookResponse(object):

    def __init__(self,response):
        self.all = {'info':[],'success':0,'fail':0}
        self.minion = response.keys()
        self.parse(response)

    def parse(self,response):
        for minion,ret in response.items():
            item = {
                'minion': None,
                'events':[],
                'code':0,
                'event_success':0,
                'event_fail':0,
            }
            item['minion'] = minion

            if type(ret) is list:
                item['code'] = 9527
                item['events'] = ret
                self.all['fail']+=1

            else:
                event_list = []
                self.all['success']+=1
                for k,v in ret.items():
                    if v['result']:
                        item['event_success']+=1
                    else:
                        item['event_fail']+=1
                    event_obj = PlaybookEvent(k,v)
                    event_list.append(event_obj)

                self.insert_sort(event_list)
                for i in event_list:
                    item['events'].append(i.__dict__)
            self.all['info'].append(item)

    def insert_sort(self,list):
        for i in range(1,len(list)):
            for j in range(i,0,-1):
                if list[j].num < list[j-1].num:
                    list[j],list[j-1] = list[j-1],list[j]
        return list