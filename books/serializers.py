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
    role = serializers.CharField(source='role.title')

    class Meta:
        model = BookContribution
        fields = ['id', 'contributor', 'role']

# Main Book Serializer
class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    contributions = BookContributionSerializer(source='bookcontribution_set', many=True, required=False)

    # Separate fields for frontend convenience
    authors = serializers.SerializerMethodField()
    publishers = serializers.SerializerMethodField()
    translators = serializers.SerializerMethodField()


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
            'cover_image',
            'contributions',
            'authors',
            'publishers',
            'translators'
        ]

    def create(self, validated_data):
        # Handle nested category
        category_data = validated_data.pop('category')
        contributions_data = validated_data.pop('bookcontribution_set', [])

        category, _ = Category.objects.get_or_create(**category_data)

        # Create book
        book = Book.objects.create(category=category, **validated_data)

        for contrib in contributions_data:
            role_title = contrib['role']['title']
            contributor_data = contrib['contributor']
            contributor, _ = Contributor.objects.get_or_create(**contributor_data)
            role, _ = Role.objects.get_or_create(title=role_title)
            BookContribution.objects.create(book=book, contributor=contributor, role=role)

        return book


    def update(self, instance, validated_data):
        # Update category if provided
        category_data = validated_data.pop('category', None)
        contributions_data = validated_data.pop('bookcontribution_set', None)


        if category_data:
            category, _ = Category.objects.get_or_create(**category_data)
            instance.category = category

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if contributions_data is not None:
            # Clear existing contributions
            BookContribution.objects.filter(book=instance).delete()
            for contrib in contributions_data:
                role_title = contrib['role']['title']
                contributor_data = contrib['contributor']
                contributor, _ = Contributor.objects.get_or_create(**contributor_data)
                role, _ = Role.objects.get_or_create(title=role_title)
                BookContribution.objects.create(book=instance, contributor=contributor, role=role)

        return instance

    # --- Helper methods to get authors, publishers, translators ---
    def get_authors(self, obj):
        contributions = BookContribution.objects.filter(book=obj, role__title__iexact='author')
        return ContributorSerializer([c.contributor for c in contributions], many=True).data

    def get_publishers(self, obj):
        contributions = BookContribution.objects.filter(book=obj, role__title__iexact='publisher')
        return ContributorSerializer([c.contributor for c in contributions], many=True).data

    def get_translators(self, obj):
        contributions = BookContribution.objects.filter(book=obj, role__title__iexact='translator')
        return ContributorSerializer([c.contributor for c in contributions], many=True).data


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