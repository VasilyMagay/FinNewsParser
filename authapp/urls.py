"""
authapp/urls.py
"""
from django.urls import re_path
import authapp.views as authapp

app_name = 'authapp'

urlpatterns = [
    re_path(r'^login/$', authapp.user_login, name='login'),
    re_path(r'^logout/$', authapp.user_logout, name='logout'),
    re_path(r'^register/$', authapp.user_register, name='register'),
    re_path(r'^update/$', authapp.user_update, name='update'),
    re_path(r'^verify/(?P<email>.+)/(?P<activation_key>\w+)/$', authapp.verify, name='verify'),
]
