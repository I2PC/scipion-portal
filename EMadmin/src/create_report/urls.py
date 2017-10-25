from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create_report$', views.create_report, name='create_report'),
    url(r'^create_report_latex/(?P<project_name>[\w\-]+)/$', views.create_report_latex,
        name='create_report_latex'),
]
