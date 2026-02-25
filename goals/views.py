from django.db.models import Sum, F
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from study_session.models import ReadingSession
from .models import ReadingGoal
from .serializers import ReadingGoalSerializer
from books.models import ReadingList


class ReadingGoalViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_goal(self, request):
        serializer = ReadingGoalSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        goal = serializer.save()

        return Response(
            ReadingGoalSerializer(goal).data,
            status=status.HTTP_201_CREATED
        )


    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        try:
            goal = ReadingGoal.objects.get(pk=pk, user=request.user)
        except ReadingGoal.DoesNotExist:
            return Response({"error": "Goal not found"}, status=404)

        sessions = ReadingSession.objects.filter(user=request.user)

        # Calculate based on type
        if goal.goal_type == 'pages':
            current_value = sessions.aggregate(
                total=Sum('pages_read')
            )['total'] or 0

        elif goal.goal_type == 'time':
            total_seconds = sum(
                session.duration.total_seconds()
                for session in sessions
            )
            current_value = total_seconds / 3600  # hours


        elif goal.goal_type == 'books':
            current_value = ReadingList.objects.filter(
                user=request.user,
                pages_read__gte=F('book__total_pages')
            ).count()

        else:
            current_value = 0

        # Calculate percentage
        percentage = 0
        if goal.target_value > 0:
            percentage = (current_value / goal.target_value) * 100

        # Auto complete
        if current_value >= goal.target_value and not goal.is_completed:
            goal.is_completed = True
            goal.save()

        return Response({
            "goal_id": goal.id,
            "goal_type": goal.goal_type,
            "target_value": goal.target_value,
            "current_value": round(current_value, 2),
            "percentage": round(percentage, 2),
            "is_completed": goal.is_completed
        })