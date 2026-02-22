import uuid
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from books.models import Book
from study_session.models import ReadingSession


class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="notes",
        null=True,
        blank=True
    )

    session = models.ForeignKey(
        ReadingSession,
        on_delete=models.CASCADE,
        related_name="notes",
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.book and not self.session:
            raise ValidationError("Note must belong to a book or a session.")

        if self.book and self.session:
            raise ValidationError("Note cannot belong to both book and session.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Note by {self.user.username}"