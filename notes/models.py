import uuid

from django.db import models
from books.models import Book
from accounts.models import Account


# Create your models here.

class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
