from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.db import models


class StandardUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, phone_number=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class StandardUser(AbstractUser):
    email = models.EmailField(blank=True)
    # Phone number is field agnostic, but it expects all numbers to be in E.164 format
    # or other configured format according to django phonenumber field settings
    phone_number = models.CharField(max_length=20, blank=False, null=True)
    username = models.CharField(max_length=150)
    USERNAME_FIELD = "username"
    objects = StandardUserManager()


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class CustomUser(AbstractBaseUser):
    custom_username = models.CharField(max_length=150)
    custom_email = models.EmailField(blank=True)
    custom_mobile = models.CharField(max_length=20, blank=True)
    custom_required_field = models.CharField(max_length=2)
    is_active = models.BooleanField(default=True)
    objects = CustomUserManager()

    EMAIL_FIELD = "custom_email"
    USERNAME_FIELD = "custom_username"
