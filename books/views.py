from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Book, Category, Contributor, Role, BookContribution
from .serializers import BookSerializer, CategorySerializer, ContributorSerializer, BookContributionSerializer

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