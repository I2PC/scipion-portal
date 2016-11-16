from django.conf.urls import url
from report_protocols import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
