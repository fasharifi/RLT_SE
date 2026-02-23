from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Book, Category, Contributor, Role, BookContribution, ReadingList, Favorite
from .serializers import BookSerializer, CategorySerializer, ContributorSerializer, BookContributionSerializer, \
    ReadingListCreateSerializer, ReadingListSerializer


class BookViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    # 1️⃣ Add a new book
    @action(detail=False, methods=['post'])
    def add_book(self, request):
        serializer = BookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = serializer.save()
        return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)

    # 2️⃣ Edit a book
    @action(detail=True, methods=['put'])
    def edit_book(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookSerializer(book, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # 3️⃣ Delete a book
    @action(detail=True, methods=['delete'])
    def delete_book(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        # Delete related contributions
        BookContribution.objects.filter(book=book).delete()
        book.delete()
        return Response({"message": "Book and related contributions deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    # 4️⃣ List all books
    @action(detail=False, methods=['get'])
    def list_books(self, request):
        books = Book.objects.all()

        # --- Filters ---
        category_id = request.query_params.get('category_id')
        publisher_id = request.query_params.get('publisher_id')  # contributor id
        search = request.query_params.get('search')

        if category_id:
            books = books.filter(category__id=category_id)

        if publisher_id:
            # filter by BookContribution where role is publisher
            books = books.filter(
                bookcontribution__role__title__iexact='publisher',
                bookcontribution__contributor__id=publisher_id
            )

        # --- Search ---
        if search:
            books = books.filter(
                Q(name__icontains=search) |
                Q(bookcontribution__role__title__iexact='author',
                  bookcontribution__contributor__firstname__icontains=search) |
                Q(bookcontribution__role__title__iexact='author',
                  bookcontribution__contributor__lastname__icontains=search) |
                Q(bookcontribution__role__title__iexact='publisher',
                  bookcontribution__contributor__firstname__icontains=search) |
                Q(bookcontribution__role__title__iexact='publisher',
                  bookcontribution__contributor__lastname__icontains=search)
            )

        books = books.distinct()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    # 5️⃣ Retrieve single book
    @action(detail=True, methods=['get'])
    def retrieve_book(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book)
        return Response(serializer.data)

class ReadingListViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # 1️⃣ Add book to reading list
    @action(detail=False, methods=['post'])
    def add(self, request):
        serializer = ReadingListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book = serializer.validated_data['book']
        pages_read = serializer.validated_data.get('pages_read', 0)
        total_hours = serializer.validated_data.get('total_hours', 0.0)

        reading_list, created = ReadingList.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={'pages_read': pages_read, 'total_hours': total_hours}
        )
        if not created:
            return Response({"error": "Book already in your reading list"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ReadingListSerializer(reading_list).data, status=status.HTTP_201_CREATED)


    # 2️⃣ Update progress (pages read / hours)
    @action(detail=True, methods=['put'])
    def update_progress(self, request, pk=None):
        try:
            entry = ReadingList.objects.get(pk=pk, user=request.user)
        except ReadingList.DoesNotExist:
            return Response({"error": "Entry not found"}, status=status.HTTP_404_NOT_FOUND)

        pages_read = request.data.get('pages_read', entry.pages_read)
        total_hours = request.data.get('total_hours', entry.total_hours)

        entry.pages_read = pages_read
        entry.total_hours = total_hours
        entry.save()
        return Response(ReadingListSerializer(entry).data)


    # 3️⃣ List all reading list entries for the user
    @action(detail=False, methods=['get'])
    def list_entries(self, request):
        entries = ReadingList.objects.filter(user=request.user)
        serializer = ReadingListSerializer(entries, many=True)
        return Response(serializer.data)


    # 4️⃣ Remove a book from reading list
    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        try:
            entry = ReadingList.objects.get(pk=pk, user=request.user)
            entry.delete()
            return Response({"message": "Book removed from reading list"}, status=status.HTTP_204_NO_CONTENT)
        except ReadingList.DoesNotExist:
            return Response({"error": "Entry not found"}, status=status.HTTP_404_NOT_FOUND)

class CategoryViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def categories(self, request):
        from .models import Category
        return Response([{"id": c.id, "title": c.title} for c in Category.objects.all()])

class ContributionViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def publishers(self, request):
        from .models import Contributor, Role
        publisher_role = Role.objects.filter(title__iexact='publisher').first()
        if not publisher_role:
            return Response([])
        publishers = Contributor.objects.filter(bookcontribution__role=publisher_role).distinct()
        return Response([{"id": p.id, "name": f"{p.firstname} {p.lastname}"} for p in publishers])

class FavoriteViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # Add to favorites
    @action(detail=False, methods=['post'])
    def add(self, request):
        book_id = request.data.get('book')

        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=404)

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            book=book
        )

        if not created:
            return Response({"error": "Book already in favorites"}, status=400)

        return Response({"message": "Added to favorites"}, status=201)

    # List user favorites
    @action(detail=False, methods=['get'])
    def list_entries(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        books = [fav.book for fav in favorites]
        serializer = BookSerializer(books, many=True, context={'request': request})
        return Response(serializer.data)

    # Remove from favorites
    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        try:
            fav = Favorite.objects.get(pk=pk, user=request.user)
            fav.delete()
            return Response({"message": "Removed from favorites"}, status=204)
        except Favorite.DoesNotExist:
            return Response({"error": "Entry not found"}, status=404)