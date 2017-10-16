from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add_acquisition$', views.add_acquisition, name='add_acquisition'),
]
