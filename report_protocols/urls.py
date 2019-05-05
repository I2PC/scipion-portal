from django.conf.urls import url, include
from report_protocols import views
from django.contrib import admin
admin.autodiscover()
from tastypie.api import Api
from api import WorkflowResource, ProtocolResource, PackageResource

# Keep this paths to allow scipion reporting
old_api = Api(api_name='workflow')
old_api.register(WorkflowResource())

new_api = Api(api_name="v2")
new_api.register(ProtocolResource())
new_api.register(PackageResource())
new_api.register(WorkflowResource())

urlpatterns = [
    url(r'^api/', include(old_api.urls)),
    url(r'^api/', include(new_api.urls)),
    url(r'^protocolTable/', views.protocolTable, name='protocolRanking'),
    url(r'^scipionUsage', views.scipionUsage, name='scipionUsage'),
    url(r'^protocoltypes', views.protocolTypes, name='protocolTypes'),
    url(r'^packages', views.packages, name='packages'),
]

