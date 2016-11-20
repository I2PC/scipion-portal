from django.conf.urls import url, include
from report_protocols import views
from django.contrib import admin
admin.autodiscover()
from tastypie.api import Api
from api import WorkflowResource, ProtocolResource

user_api = Api(api_name='workflow')
user_api.register(WorkflowResource())
user_api.register(ProtocolResource())

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/',include(user_api.urls)),
]
