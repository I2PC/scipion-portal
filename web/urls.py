from django.urls import re_path as url, include
from web import views_home
from tastypie.api import Api
from web.api import ContributionResource

api = Api(api_name="v2")
api.register(ContributionResource())


urlpatterns = [
    url(r'^$', views_home.home, name='home'),
    url(r'^download_form', views_home.download_form, name='download-page'),
    url(r'^startdownload/', views_home.startDownload, name='download'),
    url(r'^getdownloadsdata', views_home.getDownloadsStats),
    url(r'^downloadstats', views_home.showDownloadStats, name='download-stats'),
    url(r'^getplugins', views_home.getPluginsJSON),
    url(r'^acknowledgements', views_home.acknowledgements, name='acknowledgements'),
    url(r'^biologists', views_home.biologists, name='biologists'),
    url(r'^facilities', views_home.facilities, name='facilities'),
    url(r'^developers', views_home.developers, name='developers'),
    url(r'^contact', views_home.contact, name='contact'),
    url(r'^api/', include(api.urls)),
]
