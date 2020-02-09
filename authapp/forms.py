from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from authapp.models import SiteUser
import django.forms as forms
import random
import hashlib


class SiteUserLoginForm(AuthenticationForm):
    class Meta:
        model = SiteUser
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # вызов метода родительского класса
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  # добавляем всем элементам класс с таким именем


class SiteUserRegisterForm(UserCreationForm):
    class Meta:
        model = SiteUser
        fields = ('username', 'first_name', 'password1', 'password2', 'email', 'age')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''

    def clean_age(self):  # автоматически вызывается метод clean, когда выодятся неверные данные (для каждого поля)
        data = self.cleaned_data['age']
        if data < 18:
            raise forms.ValidationError("Вы слишком молоды!")

        return data

    def save(self):
        user = super().save()
        user.is_active = False
        # salt - модификатор
        salt = hashlib.sha1(str(random.random()).encode('utf8')).hexdigest()[:6]
        user.activation_key = hashlib.sha1((user.email + salt).encode('utf8')).hexdigest()
        user.save()

        return user


class SiteUserChangeForm(UserChangeForm):
    class Meta:
        model = SiteUser
        fields = ('username', 'first_name', 'last_name', 'password', 'email', 'age', 'is_staff')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''
            if field_name == 'password':  # спрятать поле с паролем
                field.widget = forms.HiddenInput()

    def clean_age(self):  # автоматически вызывается метод clean, когда выодятся неверные данные (для каждого поля)
        data = self.cleaned_data['age']
        if data < 18:
            raise forms.ValidationError("Вы слишком молоды!")

        return data
