from django.urls import re_path as url, include
from report_protocols import views
from django.contrib import admin
admin.autodiscover()
from tastypie.api import Api
from report_protocols.api import WorkflowResource, ProtocolResource, PackageResource, InstallationResource

# Keep this paths to allow scipion reporting
old_api = Api(api_name='workflow')
old_api.register(WorkflowResource())
old_api.register(ProtocolResource())

# Access through api/v2 url
new_api = Api(api_name="v2")
new_api.register(ProtocolResource())
new_api.register(PackageResource())
new_api.register(WorkflowResource())
new_api.register(InstallationResource())

urlpatterns = [
    url(r'^api/', include(old_api.urls)),
    url(r'^api/', include(new_api.urls)),
    url(r'^protocolTable/', views.protocolTable, name='protocolRanking'),
    url(r'projectStats', views.projectStats, name='projectStats'),
    url(r'installationStats', views.installationStats, name='installationStats'),
    url(r'^protocoltypes', views.protocolTypes, name='protocolTypes'),
    url(r'^packages', views.packages, name='packages'),
]

