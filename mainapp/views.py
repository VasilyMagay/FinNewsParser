"""
mainapp/views.py
"""
from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic import ListView, CreateView

from mainapp.models import Site, News, Topic


def index(request):
    """
    Основная страница
    :param request:
    :return: render
    """
    sites = Site.objects.all()

    context = {
        'page_title': 'Financial News Parser',
        'sites': sites,
    }
    return render(request, 'mainapp/index.html', context)


def site(request, pkey=None):
    """
    Отображение новостей выбранного финансового сайта
    :param request:
    :param pkey:
    :return: render
    """
    if pkey is None:
        index(request)

    news = News.objects.filter(site__pk=pkey).order_by('-news_date')

    context = {
        'page_title': 'Financial News Parser',
        'news': news,
    }
    return render(request, 'mainapp/news.html', context)


class TopicList(ListView):  # pylint: disable=too-many-ancestors
    """
    Вывод списка топиков
    """
    model = Topic
    template_name = 'mainapp/topic_list.html'

    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    # def get_queryset(self):
    #     return self.request.user.topic_set.all()


class TopicCreate(CreateView):  # pylint: disable=too-many-ancestors
    """
    Добавление топика
    """
    model = Topic
    # template_name = 'mainapp/topic_update.html'
    success_url = reverse_lazy('main:topic_list')
    fields = '__all__'
