"""
mainapp/admin.py
"""
from django.contrib import admin
from .models import Site, Topic, News

admin.site.register(Site)
admin.site.register(Topic)
admin.site.register(News)
