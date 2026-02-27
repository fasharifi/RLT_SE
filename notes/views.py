from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def add_note(self, request):
        serializer = NoteSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        note = serializer.save()
        return Response(
            NoteSerializer(note).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['put'])
    def edit_note(self, request, pk=None):
        try:
            note = Note.objects.get(pk=pk, user=request.user)
        except Note.DoesNotExist:
            return Response({"error": "Note not found"}, status=404)

        import copy
        data = copy.deepcopy(request.data)

        if 'book' in data and data['book'] == '':
            del data['book']
        if 'session' in data and data['session'] == '':
            del data['session']

        print("=" * 50)
        print("EDIT NOTE REQUEST:")
        print(f"PK: {pk}")
        print(f"Original data: {request.data}")
        print(f"Cleaned data: {data}")
        print(f"Existing note - book: {note.book_id}, session: {note.session_id}")
        print("=" * 50)

        serializer = NoteSerializer(
            note,
            data=data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=400)

    @action(detail=True, methods=['delete'])
    def delete_note(self, request, pk=None):
        try:
            note = Note.objects.get(pk=pk, user=request.user)
        except Note.DoesNotExist:
            return Response({"error": "Note not found"}, status=404)

        note.delete()
        return Response(
            {"message": "Note deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get'])
    def list_notes(self, request):
        notes = Note.objects.filter(user=request.user)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)
