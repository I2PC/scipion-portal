from django.conf.urls import url, include
from report_protocols import views
from django.contrib import admin
admin.autodiscover()
from tastypie.api import Api
from api import sendMsgResource


sendSMS_api = Api(api_name='sendSMS')
sendSMS_api.register(sendMsgResource())

urlpatterns = [
    url(r'^api/',include(sendSMS_api.urls)),
]
