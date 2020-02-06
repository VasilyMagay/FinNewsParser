from django.shortcuts import render


def index(request):

    context = {
        'page_title': 'Financial News Parser',
    }
    return render(request, 'mainapp/index.html', context)
