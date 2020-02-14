from django.db import models
from authapp.models import SiteUser


class Site(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    ref = models.CharField(max_length=1024, verbose_name='Reference')


class Topic(models.Model):
    user = models.ForeignKey(SiteUser, verbose_name='User', on_delete=models.CASCADE)
    site = models.ForeignKey(Site, verbose_name='Site', on_delete=models.CASCADE)

    name = models.CharField(max_length=200, verbose_name='Name')
    keywords = models.CharField(max_length=1024, verbose_name='Keywords, phrases')
    inactive = models.BooleanField(verbose_name='Inactive')
    period_start = models.DateTimeField(blank=True, null=True, verbose_name='Active Period Start')
    period_end = models.DateTimeField(blank=True, null=True, verbose_name='Active Period End')


class News(models.Model):
    user = models.ForeignKey(SiteUser, verbose_name='User', on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, verbose_name='Topic', on_delete=models.CASCADE)

    news_date = models.DateTimeField(blank=True, null=True, verbose_name='News date')
    ref = models.CharField(max_length=1024, verbose_name='Reference')
    brief_info = models.TextField(blank=True, verbose_name='Brief')
