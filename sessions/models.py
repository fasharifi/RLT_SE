import uuid
from django.db import models
from books.models import Book
from accounts.models import Account


# Create your models here.


class StudySession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    pages_read = models.PositiveIntegerField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

