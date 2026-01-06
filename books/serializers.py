from rest_framework import serializers
from .models import Book, Category, Contributor, BookContribution

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'name', 'isbn', 'description', 'total_pages', 'category']

class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'firstname', 'lastname', 'birthdate', 'country']

class BookContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookContribution
        fields = ['id', 'role', 'contributor', 'book']