from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^add_acquisition$', views.add_acquisition, name='add_acquisition'),
    url(r'^add_acquisition2$', views.add_acquisition2, name='add_acquisition2'),


]
