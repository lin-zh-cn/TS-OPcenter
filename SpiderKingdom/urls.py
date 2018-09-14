from django.conf.urls import url
from django.conf.urls import include
from SpiderKingdom import views

from rest_framework import routers
from SpiderKingdom import views

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)
router.register(r'domains', views.DomainViewSet)
router.register(r'slave_get', views.SlaveGetViewSet)
router.register(r'slave_post', views.SlavePostViewSet)
router.register(r'projects', views.ProjectViewSet)
# router.register(r'status_codes', views.StatusCodeViewSet)
router.register(r'cdns', views.CDNViewSet)
router.register(r'nodes', views.NodeViewSet)
router.register(r'cert', views.CertViewSet)
router.register(r'faillog', views.FailLogViewSet)


urlpatterns = [
    # url(r'^api/domain', views.domain),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/chart/(?P<domain_id>\d+)/',views.MonitorDataList.as_view({'get':'list'})),
    url(r'^api/domain_to_node/(?P<node_id>\d+)/',views.Domain_To_NodeSet.as_view({'put':'update','get':'list'}))

]