from rest_framework import viewsets, permissions
from .models import Goal, GoalBook
from .serializers import GoalSerializer, GoalBookSerializer


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]


class GoalBookViewSet(viewsets.ModelViewSet):
    queryset = GoalBook.objects.all()
    serializer_class = GoalBookSerializer
    permission_classes = [permissions.IsAuthenticated]
