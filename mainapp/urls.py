"""
mainapp/urls.py
"""
from django.urls import re_path
import mainapp.views as mainapp

app_name = 'mainapp'

urlpatterns = [
    re_path(r'^$', mainapp.index, name='index'),
    re_path(r'^news/(\d+)/$', mainapp.site, name='site'),
    re_path(r'^topics/$', mainapp.TopicList.as_view(), name='topic_list'),
    re_path(r'^topics/create/$', mainapp.TopicCreate.as_view(), name='topic_create'),
    # re_path(r'^topics/remove/(<int:pk>)/$', mainapp.topic_remove, name='topic_remove'),
]
