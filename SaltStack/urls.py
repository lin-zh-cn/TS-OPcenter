from django.conf.urls import url
from django.conf.urls import include
from rest_framework import routers
router = routers.DefaultRouter()
from SaltStack import views

router.register(r'group', views.GroupsViewset, base_name="分组")
router.register(r'minion', views.MinionsViewset, base_name="主机")
router.register(r'minion_test',views.Mnion_Test, base_name="主机在线检测")
router.register(r'minion_grains',views.Mnion_Grains, base_name="主机配置检测")
router.register(r'playbook', views.PlaybooksViewset, base_name="剧本")
router.register(r'playbook_previous', views.PlaybooksPreviousViewset, base_name="剧本旧版本")
router.register(r'jobs',views.JobsViewset, base_name="剧本执行")

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api/unminion/',views.MinionsUnacceptedViewset.as_view({'get':'list'})),
]


# url(r'^minion_list/$', views.minion_list),
# url(r'^minion_list/(\d+)/$', views.minion_list),
# url(r'^minion_add/$', views.minion_add),
# url(r'^minion_test/$', views.minion_test),
# url(r'^minion_del/$', views.minion_del),
# url(r'^minion_search/$', views.minion_search),
# url(r'^minion_search/(\d?)/$', views.minion_search),
# # 剧本管理和操作
# url(r'^playbook/$', views.playbook),
# url(r'^playbook/(.*)/$', views.playbook_project),
# url(r'^playbook_upload/$', views.playbook_upload),
# url(r'^playbook_edit/$', views.playbook_edit),
# url(r'^playbook_save/$', views.playbook_save),
# url(r'^playbook_del/$', views.playbook_del),
# url(r'^playbook_exe/$', views.playbook_exe),
# url(r'^playbook_exe/(.*)/(\d+)/$', views.playbook_exe),
#
# url(r'^playbook_exe_sls/$', views.playbook_exe_sls),
# url(r'^playbook_exe_ret/$', views.playbook_exe_ret),
# url(r'^playbook_exe_ret/(\d+)/$', views.playbook_exe_ret),
# # 远程终端

