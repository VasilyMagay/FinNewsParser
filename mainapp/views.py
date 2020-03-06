from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.views.generic import ListView, CreateView
from mainapp.models import Site, News, Topic
from django.urls import reverse_lazy


def index(request):
    sites = Site.objects.all()

    context = {
        'page_title': 'Financial News Parser',
        'sites': sites,
    }
    return render(request, 'mainapp/index.html', context)


def site(request, pk=None):
    if pk is None:
        index(request)

    news = News.objects.filter(site__pk=pk).order_by('-news_date')

    context = {
        'page_title': 'Financial News Parser',
        'news': news,
    }
    return render(request, 'mainapp/news.html', context)


class TopicList(ListView):
    model = Topic
    template_name = 'mainapp/topic_list.html'

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    # def get_queryset(self):
    #     return self.request.user.topic_set.all()


class TopicCreate(CreateView):
    model = Topic
    # template_name = 'mainapp/topic_update.html'
    success_url = reverse_lazy('main:topic_list')
    fields = '__all__'
