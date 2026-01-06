import uuid

from django.contrib.auth.models import User
from django.db import models
from books.models import Book


# Create your models here.


class StudySession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    pages_read = models.PositiveIntegerField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)