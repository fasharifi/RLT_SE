import uuid
from django.contrib.auth.models import User
from django.db import models
from django.core import validators


# Create your models here.

class Permission(models.Model):
    name = models.CharField(max_length=10, verbose_name="نوع دسترسی", null=True, blank=False, default="basic")

    def __str__(self):
        return self.name


class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='active_session')
    token = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class Role(models.Model):
    name = models.CharField(max_length=20, null=True, blank=False, default="student")
    permissions = models.ManyToManyField(Permission)

    def __str__(self):
        return self.name

    def get_permission(self, permission):
        return self.permissions.filter(name=permission).exists()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=45, null=True, blank=False)
    last_name = models.CharField(max_length=45, null=True, blank=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=1)
    birthdate = models.CharField(max_length=10, verbose_name="تاریخ تولد", null=True, blank=False)
    phone_number = models.CharField(max_length=11, verbose_name="شماره تلفن", null=True, blank=False,
                                    validators=[validators.RegexValidator(regex='^[0-9]{11}$',
                                                                          message='شماره تلفن باید 11 رقمی باشد',
                                                                          code='invalid_phone_number')])

    def __str__(self):
        return f"{self.user.username}"


class SMSVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
