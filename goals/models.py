import uuid

from django.contrib.auth.models import User
from django.db import models
from books.models import Book


class ReadingGoal(models.Model):
    GOAL_TYPES = (
        ('pages', 'Pages'),
        ('books', 'Books'),
        ('time', 'Time'),  # hours
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    target_value = models.PositiveIntegerField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
