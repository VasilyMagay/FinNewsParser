from django.shortcuts import render, HttpResponseRedirect
from authapp.forms import SiteUserLoginForm, SiteUserRegisterForm, SiteUserChangeForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from django.core.mail import send_mail
from django.conf import settings
from authapp.models import SiteUser


def user_login(request):
    next = request.GET['next'] if 'next' in request.GET.keys() else ''

    if request.method == 'POST':
        form = SiteUserLoginForm(data=request.POST)
        if form.is_valid():
            print('форма заполнена корректно')
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                print('залогинились')
                # if 'next' in request.POST.keys():
                if 'next' in request.POST.keys() and request.POST['next']:
                    return HttpResponseRedirect(request.POST['next'])
                else:
                    return HttpResponseRedirect(reverse('main:index'))
                # return HttpResponseRedirect(reverse('main:index'))

    else:
        form = SiteUserLoginForm()

    context = {
        'form': form,
        'next': next,
    }
    return render(request, 'authapp/login.html', context)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('main:index'))


def user_register(request):
    if request.method == 'POST':
        form = SiteUserRegisterForm(request.POST, request.FILES)
        # ВАЖНО указать request.FILES - данные для загрузки на сервер,
        # А на форме должно быть указано свойство enctype="multipart/form-data"
        if form.is_valid():
            user = form.save()
            if send_verify_mail(user):
                print('сообщение подтверждения отправлено')
                return HttpResponseRedirect(reverse('main:index'))
            else:
                print('ошибка отправки сообщения')
                return HttpResponseRedirect(reverse('auth:login'))
            return HttpResponseRedirect(reverse('main:index'))
    else:
        form = SiteUserRegisterForm()

    context = {
        'form': form,
        'title': 'регистрация',
    }
    return render(request, 'authapp/register.html', context)


def user_update(request):
    if request.method == 'POST':
        edit_form = SiteUserChangeForm(request.POST, request.FILES, instance=request.user)
        if edit_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse('auth:update'))
    else:
        edit_form = SiteUserChangeForm(instance=request.user)

    content = {
        'title': 'редактирование',
        'edit_form': edit_form,
    }

    return render(request, 'authapp/edit.html', content)


def send_verify_mail(user):
    verify_link = reverse('auth:verify', args=[user.email, user.activation_key])

    title = f'Подтверждение учетной записи {user.username}'

    message = f'Для подтверждения учетной записи {user.username} на портале {settings.DOMAIN_NAME} ' \
              f'перейдите по ссылке: \n{settings.DOMAIN_NAME}{verify_link}'

    return send_mail(title, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)


def verify(request, email, activation_key):
    try:
        user = SiteUser.objects.get(email=email)
        if user.activation_key == activation_key and not user.is_activation_key_expired():
            user.is_active = True
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        else:
            print(f'error activation user: {user}')
        return render(request, 'authapp/verification.html')
    except Exception as e:
        print(f'error activation user: {e} -> {e.args}')
        return HttpResponseRedirect(reverse('main:index'))
