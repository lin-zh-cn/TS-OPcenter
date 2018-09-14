from django.conf.urls import url
from django.conf.urls import include
from Azeroth import views


urlpatterns = [
    url(r'^login', views.login),
]