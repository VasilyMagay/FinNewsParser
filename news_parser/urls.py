"""news_parser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# from django.urls import path
from django.urls import re_path, include

# import mainapp

urlpatterns = [
    re_path(r'^', include('mainapp.urls', namespace='main')),
    re_path(r'^auth/', include('authapp.urls', namespace='auth')),
    re_path(r'^admin/', admin.site.urls),  # типовая админка
    # re_path(r'^news/', include('mainapp.urls', namespace='news')),
    # re_path(r'^topics/', include('mainapp.urls', namespace='topics')),
    # re_path(r'^admin/', include('adminapp.urls', namespace='admin')),
    # re_path(r'^auth/verify/google/oauth2/', include('social_django.urls', namespace='social')),
]
# re_path(r'^(\d+)/$', mainapp.site, name='site'),
