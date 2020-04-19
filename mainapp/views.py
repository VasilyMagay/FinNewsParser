"""
mainapp/views.py
"""
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test

from mainapp.models import Site, News, Topic, TopicSite
from mainapp.forms import TopicEditForm, TopicSiteEditForm


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

    news = News.objects.filter(site__pk=pkey).order_by('-news_date')[:20]
    current_site = Site.objects.get(pk=pkey)
    site_name = current_site.name if current_site else ''
    context = {
        'page_title': 'Financial News Parser',
        'news': news,
        'site_name': site_name,
    }
    return render(request, 'mainapp/news.html', context)


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class TopicsListView(ListView):
    """
    Вывод списка топиков
    """
    model = Topic
    template_name = 'mainapp/topic_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'FNP: Список топиков'
        return context

    def get_ordering(self):
        return ['name']

    def get_queryset(self):
        return self.request.user.topic_set.all()


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class TopicCreateView(CreateView):
    """
    Добавление топика
    """
    model = Topic
    form_class = TopicEditForm
    # template_name = 'mainapp/topic_update.html'
    success_url = reverse_lazy('main:topics')

    # fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'FNP: Новый топик'
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class TopicUpdateView(UpdateView):
    model = Topic
    success_url = reverse_lazy('main:topics')
    form_class = TopicEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'FNP: Изменение топика'
        return context


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class TopicDeleteView(DeleteView):
    model = Topic
    success_url = reverse_lazy('main:topics')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'FNP: Удаление топика'
        return context


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class TopicSitesListView(ListView):
    model = TopicSite
    topic = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # print('CONTEXT==', self.category)
        context['page_title'] = 'FNP: Сайты топика'
        context['topic'] = get_object_or_404(Topic, pk=self.topic)
        return context

    def get_ordering(self):
        return ['name']

    def get_queryset(self):
        # print('KWARGS=', self.kwargs['pk'])
        self.topic = self.kwargs['pk']
        return TopicSite.objects.filter(topic__pk=self.topic)


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class TopicSiteCreateView(CreateView):
    model = TopicSite
    topic = None
    # success_url = reverse_lazy('admin:products')
    form_class = TopicSiteEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'FNP: Новый сайт топика'
        context['topic'] = get_object_or_404(Topic, pk=self.topic)
        return context

    def get_initial(self):
        self.topic = self.kwargs['pk']
        initial = self.initial.copy()
        initial['topic'] = self.topic
        return initial

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(reverse('main:topic_sites', kwargs={'pk': self.topic}))


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class TopicSiteDeleteView(DeleteView):
    model = TopicSite
    success_url = reverse_lazy('main:topics')  # TODO: Нужен переход на список сайтов выбранного топика

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'FNP: Удаление сайта топика'
        return context
