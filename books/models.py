import uuid

from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

# Create your models here.
class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    isbn = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_pages = models.PositiveIntegerField()

    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)



class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)


class Contributor(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    birthdate = models.DateField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class BookContribution(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    contributor = models.ForeignKey(Contributor,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('role', 'contributor', 'book')


class ReadingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="in_reading_lists")
    pages_read = models.PositiveIntegerField(default=0)
    total_hours = models.FloatField(default=0.0)  # total hours spent reading
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'book')


