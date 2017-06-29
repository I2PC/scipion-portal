from django.conf.urls import url
from web import views_home

urlpatterns = [
    url(r'^$', views_home.home),
    url(r'^download_form', views_home.download_form, name='download_form'),
    url(r'^startdownload/', views_home.startDownload),
    url(r'^download/', views_home.doDownload),
    url(r'^getdownloadsdata', views_home.getDownloadsStats),
    url(r'^downloadstats', views_home.showDownloadStats),
]
