from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Book, Category, Contributor, Role, BookContribution, ReadingList
from .serializers import BookSerializer, CategorySerializer, ContributorSerializer, BookContributionSerializer, \
    ReadingListCreateSerializer, ReadingListSerializer


class BookViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

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