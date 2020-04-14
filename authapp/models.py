"""
authapp/models.py
"""
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


def get_now():
    """
    Возвращает текущую дату плюс два дня.
    :return: date
    """
    return now() + timedelta(hours=48)


class SiteUser(AbstractUser):
    """
    Класс SiteUser
    """
    age = models.PositiveIntegerField(verbose_name='Age', null=True)
    activation_key = models.CharField(max_length=128, blank=True)
    activation_key_expires = models.DateTimeField(default=get_now())

    def is_activation_key_expired(self):
        return now() > self.activation_key_expires
