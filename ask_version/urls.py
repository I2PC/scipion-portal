from django.conf.urls import url
from ask_version import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
