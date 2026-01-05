import uuid
from django.db import models
from accounts.models import Account
from books.models import Book


# Create your models here.

class Goal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_value = models.IntegerField()
    progress = models.DecimalField(max_digits=5, decimal_places=2)
    deadline = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

class GoalBook(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
