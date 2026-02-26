import uuid
from django.contrib.auth.models import User
from django.db import models


class ReadingGoal(models.Model):
    GOAL_TYPES = (
        ('pages', 'Pages'),
        ('books', 'Books'),
        ('time', 'Time'),  # hours
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    target_value = models.PositiveIntegerField(help_text="Target number of pages/books/hours")
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'goal_type'],
                condition=models.Q(is_completed=False),
                name='unique_active_goal_per_type'
            )
        ]

    def __str__(self):
        return f"{self.get_goal_type_display()} - {self.target_value} ({'Completed' if self.is_completed else 'Active'})"
