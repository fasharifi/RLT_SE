from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ReadingSession
from .serializers import ReadingSessionSerializer
from books.models import ReadingList


class ReadingSessionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def add_session(self, request):
        serializer = ReadingSessionSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        return Response(
            ReadingSessionSerializer(session).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['put'])
    def edit_session(self, request, pk=None):
        try:
            session = ReadingSession.objects.get(pk=pk, user=request.user)
        except ReadingSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=404)

        serializer = ReadingSessionSerializer(
            session,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def delete_session(self, request, pk=None):
        try:
            session = ReadingSession.objects.get(pk=pk, user=request.user)
        except ReadingSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=404)

        # Update stats before deleting
        reading_list = ReadingList.objects.get(user=request.user, book=session.book)

        reading_list.pages_read -= session.pages_read
        reading_list.total_hours -= session.duration.total_seconds() / 3600
        reading_list.save()

        session.delete()

        return Response(
            {"message": "Session deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get'])
    def list_sessions(self, request):
        sessions = ReadingSession.objects.filter(user=request.user)
        serializer = ReadingSessionSerializer(sessions, many=True)
        return Response(serializer.data)