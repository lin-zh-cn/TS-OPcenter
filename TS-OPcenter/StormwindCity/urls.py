from django.conf.urls import url
from django.conf.urls import include


from rest_framework import routers
from StormwindCity import views

router = routers.DefaultRouter()
# router.registry(r'login',views.TrustAsia_apply)


urlpatterns = [
    url(r'^api/freessl/', include(router.urls)),
    url(r'^api/freessl/login/',views.TrustAsia_apply),
    url(r'^api/freessl/create_order/',views.TrustAsia_apply_create_order),
    url(r'^api/freessl/order_authz/',views.TrustAsia_apply_Order_Authz),
    url(r'^api/freessl/download_nginx/(.*)/',views.TrustAsia_download_nginx),
    url(r'^api/freessl/download_iis/(.*)/',views.TrustAsia_download_iis),
    url(r'^api/freessl/order_list/',views.TrustAsia_order_list),
    url(r'^api/freessl/cert_list/',views.TrustAsia_cert_list),
    url(r'^api/freessl/order_detail/',views.TrustAsia_order_detail),
    url(r'^api/freessl/order_delete/',views.TrustAsia_order_delete),
    url(r'^api/freessl/cert_detail/',views.TrustAsia_cert_detail),
    url(r'^api/freessl/cert_delete/',views.TrustAsia_cert_delete),
    url(r'^api/freessl/cert_select/',views.TrustAsia_cert_select),
    url(r'^api/cert_check/myssl/',views.myssl_check),
    url(r'^api/cert_check/sslsechi/',views.sslceshi_check),
]