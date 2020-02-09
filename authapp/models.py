from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from datetime import timedelta


def get_now():
    return now() + timedelta(hours=48)


class SiteUser(AbstractUser):
    age = models.PositiveIntegerField(verbose_name='Age', null=True)
    activation_key = models.CharField(max_length=128, blank=True)
    activation_key_expires = models.DateTimeField(default=get_now())

    def is_activation_key_expired(self):
        return now() > self.activation_key_expires
