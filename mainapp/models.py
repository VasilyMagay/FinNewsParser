from django.db import models


# class Site(models.Model):
#     name = models.CharField(max_length=200, verbose_name='наименование')
#     ref = models.CharField(max_length=1024, verbose_name='ссылка на ресурс')
#
#
# class Topic(models.Model):
#     name = models.CharField(max_length=200, verbose_name='наименование темы')
#     keywords = models.CharField(max_length=1024, verbose_name='ключевые слова, фразы')
#     is_off = models.BooleanField(verbose_name='тема отключена')
#     site = models.ForeignKey(Site, verbose_name='сайт', on_delete=models.CASCADE)
#
#     choice = models.CharField(max_length=200)
#     votes = models.IntegerField()
