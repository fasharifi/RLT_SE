from rest_framework import viewsets, permissions
from .models import StudySession
from .serializers import StudySessionSerializer


class StudySessionViewSet(viewsets.ModelViewSet):
    queryset = StudySession.objects.all()
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]
