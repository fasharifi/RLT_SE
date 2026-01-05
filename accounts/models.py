import uuid

from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserSession(models.Model):
    # Allow multiple concurrent sessions per user by using a ForeignKey
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sessions",
        db_index=True,
    )
    # Token associated with this session.  Consider storing a hash instead
    # of the raw token in production.
    token = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"



class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    phonenumber = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
