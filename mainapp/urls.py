"""
mainapp/urls.py
"""
from django.urls import re_path
import mainapp.views as mainapp

app_name = 'mainapp'

urlpatterns = [
    re_path(r'^$', mainapp.index, name='index'),
    re_path(r'^news/(\d+)/$', mainapp.site, name='site'),

    re_path(r'^topics/$', mainapp.TopicsListView.as_view(), name='topics'),
    re_path(r'^topic/create/$', mainapp.TopicCreateView.as_view(), name='topic_create'),
    re_path(r'^topic/update/(?P<pk>\d+)/$', mainapp.TopicUpdateView.as_view(), name='topic_update'),
    re_path(r'^topic/delete/(?P<pk>\d+)/$', mainapp.TopicDeleteView.as_view(), name='topic_delete'),

    re_path(r'^topic_sites/(?P<pk>\d+)/$', mainapp.TopicSitesListView.as_view(), name='topic_sites'),
    re_path(r'^topic_site/create/(?P<pk>\d+)/$', mainapp.TopicSiteCreateView.as_view(), name='topicsite_create'),
    re_path(r'^topic_site/delete/(?P<pk>\d+)/$', mainapp.TopicSiteDeleteView.as_view(), name='topicsite_delete'),

]
