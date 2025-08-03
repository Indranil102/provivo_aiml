# user/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    group = models.ForeignKey(
        'chat.Group',
        on_delete=models.CASCADE,
        null=False,     # must choose
        blank=False
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        swappable = 'AUTH_USER_MODEL'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    google_calendar_token = models.TextField(blank=True, null=True)
    google_refresh_token = models.TextField(blank=True, null=True)