from django.db import models
from authapp.models import SiteUser


class Site(models.Model):
    """
    Список сайтов, которые можем обрабатывать.
    """
    name = models.CharField(max_length=200, verbose_name='Name', null=False, unique=True)
    ref = models.CharField(max_length=1024, verbose_name='Reference', null=False)
    descr = models.CharField(max_length=1024, verbose_name='Description', null=True)


class Topic(models.Model):
    """
    Список новостных тем, которые настраивает пользователь
    """
    user = models.ForeignKey(SiteUser, verbose_name='User', on_delete=models.CASCADE)

    name = models.CharField(max_length=200, verbose_name='Topic Name')
    keywords = models.CharField(max_length=1024, verbose_name='Keywords, phrases')
    inactive = models.BooleanField(verbose_name='Inactive')
    period_start = models.DateTimeField(blank=True, null=True, verbose_name='Active Period Start')
    period_end = models.DateTimeField(blank=True, null=True, verbose_name='Active Period End')


class News(models.Model):
    """
    Общая лента всех новостей
    """
    site = models.ForeignKey(Site, verbose_name='Site', on_delete=models.CASCADE, null=True)

    news_date = models.DateTimeField(blank=True, verbose_name='News date')
    ref = models.CharField(max_length=1024, blank=False, verbose_name='Reference')
    brief_info = models.TextField(blank=True, verbose_name='Brief')
    info = models.TextField(blank=True, verbose_name='News')


class TopicSite(models.Model):
    """
    Сайты, подлежащие обработке для топика
    """
    topic = models.ForeignKey(Topic, verbose_name='Topic', on_delete=models.CASCADE)
    site = models.ForeignKey(Site, verbose_name='Site', on_delete=models.CASCADE)
