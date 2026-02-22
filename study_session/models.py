import uuid
from django.contrib.auth.models import User
from django.db import models
from books.models import Book
from django.core.exceptions import ValidationError
from datetime import timedelta


class ReadingSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.DurationField(editable=False)
    pages_read = models.PositiveIntegerField()
    note = models.TextField(blank=True, null=True)

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="sessions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def save(self, *args, **kwargs):
        self.clean()
        self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.book.name}"