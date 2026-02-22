from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # 1️⃣ Add note
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

    # 2️⃣ Edit note
    @action(detail=True, methods=['put'])
    def edit_note(self, request, pk=None):
        try:
            note = Note.objects.get(pk=pk, user=request.user)
        except Note.DoesNotExist:
            return Response({"error": "Note not found"}, status=404)

        serializer = NoteSerializer(
            note,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    # 3️⃣ Delete note
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

    # 4️⃣ List user notes
    @action(detail=False, methods=['get'])
    def list_notes(self, request):
        notes = Note.objects.filter(user=request.user)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)