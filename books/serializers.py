from rest_framework import serializers
from .models import Book, Category, Contributor, Role, BookContribution, ReadingList


# Serializer for Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

# Serializer for Contributor
class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'firstname', 'lastname', 'birthdate', 'country']

# Serializer for Role
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'title']

# Serializer for BookContribution
class BookContributionSerializer(serializers.ModelSerializer):
    contributor = ContributorSerializer()
    role = RoleSerializer()

    class Meta:
        model = BookContribution
        fields = ['id', 'contributor', 'role']

# Main Book Serializer
class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    contributions = BookContributionSerializer(source='bookcontribution_set', many=True, required=False)

    class Meta:
        model = Book
        fields = [
            'id',
            'name',
            'description',
            'isbn',
            'total_pages',
            'category',
            'created_at',
            'updated_at',
            'contributions'
        ]

    def create(self, validated_data):
        # Handle nested category
        category_data = validated_data.pop('category')
        category, _ = Category.objects.get_or_create(**category_data)

        # Create book
        book = Book.objects.create(category=category, **validated_data)
        return book

    def update(self, instance, validated_data):
        # Update category if provided
        category_data = validated_data.pop('category', None)
        if category_data:
            category, _ = Category.objects.get_or_create(**category_data)
            instance.category = category

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ReadingListSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)  # Show full book details

    class Meta:
        model = ReadingList
        fields = ['id', 'book', 'pages_read', 'total_hours', 'added_at', 'updated_at']

# Serializer for creating/updating a reading list entry
class ReadingListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingList
        fields = ['book', 'pages_read', 'total_hours']