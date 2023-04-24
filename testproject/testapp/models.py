from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class CustomUser(AbstractBaseUser):
    custom_username = models.CharField(max_length=150)
    custom_email = models.EmailField(blank=True)
    custom_mobile = models.CharField(max_length=20, blank=True)
    custom_required_field = models.CharField(max_length=2)
    is_active = models.BooleanField(default=True)

    EMAIL_FIELD = "custom_email"
    USERNAME_FIELD = "custom_username"
