from django.db.models import Sum, F, Q
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from study_session.models import ReadingSession
from books.models import ReadingList, Book
from .models import ReadingGoal
from .serializers import ReadingGoalSerializer


class ReadingGoalViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReadingGoal.objects.filter(user=self.request.user)

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
            goal = self.get_queryset().get(pk=pk)
        except ReadingGoal.DoesNotExist:
            return Response(
                {"error": "Goal not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        sessions = ReadingSession.objects.filter(user=request.user)

        current_value = 0
        details = {}

        if goal.goal_type == 'pages':
            result = sessions.aggregate(total=Sum('pages_read'))
            current_value = result['total'] or 0

            details = {
                'total_sessions': sessions.count(),
                'average_per_session': round(current_value / sessions.count(), 1) if sessions.exists() else 0
            }

        elif goal.goal_type == 'time':
            total_seconds = 0
            for session in sessions:
                if session.duration:
                    total_seconds += session.duration.total_seconds()

            current_value = total_seconds / 3600  # Convert to hours
            current_value = round(current_value, 2)

            details = {
                'total_sessions': sessions.count(),
                'total_minutes': round(total_seconds / 60, 1),
                'average_session_minutes': round(total_seconds / 60 / sessions.count(), 1) if sessions.exists() else 0
            }

        elif goal.goal_type == 'books':
            completed_books = ReadingList.objects.filter(
                user=request.user,
                pages_read__gte=F('book__total_pages')
            ).select_related('book')

            current_value = completed_books.count()

            details = {
                'completed_books': [
                    {
                        'id': entry.book.id,
                        'name': entry.book.name,
                        'completed_date': entry.updated_at
                    }
                    for entry in completed_books[:5]  # Show last 5
                ],
                'in_progress_books': ReadingList.objects.filter(
                    user=request.user,
                    pages_read__gt=0,
                    pages_read__lt=F('book__total_pages')
                ).count()
            }

        percentage = 0
        if goal.target_value > 0:
            percentage = (current_value / goal.target_value) * 100
            percentage = round(min(percentage, 100), 2)  # Cap at 100%

        was_completed = goal.is_completed
        if current_value >= goal.target_value and not goal.is_completed:
            goal.is_completed = True
            goal.save()

            completion_message = "🎉 Congratulations! You've reached your goal!"
        else:
            completion_message = None

        response_data = {
            "goal_id": goal.id,
            "goal_type": goal.goal_type,
            "goal_type_display": goal.get_goal_type_display(),
            "target_value": goal.target_value,
            "current_value": current_value,
            "percentage": percentage,
            "is_completed": goal.is_completed,
            "created_at": goal.created_at,
            "days_active": (timezone.now().date() - goal.created_at.date()).days,
            "details": details
        }

        if completion_message:
            response_data["message"] = completion_message

        return Response(response_data)

    @action(detail=False, methods=['get'])
    def list_goals(self, request):
        """
        List all goals for the user
        Can filter by completion status
        """
        goals = self.get_queryset()

        # Optional filters
        show_completed = request.query_params.get('completed')
        if show_completed is not None:
            is_completed = show_completed.lower() == 'true'
            goals = goals.filter(is_completed=is_completed)

        goal_type = request.query_params.get('type')
        if goal_type:
            goals = goals.filter(goal_type=goal_type)

        serializer = ReadingGoalSerializer(goals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        try:
            goal = self.get_queryset().get(pk=pk)
        except ReadingGoal.DoesNotExist:
            return Response(
                {"error": "Goal not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if goal.is_completed:
            return Response(
                {"error": "Goal is already completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        goal.is_completed = True
        goal.save()

        return Response({
            "message": "Goal marked as completed",
            "goal": ReadingGoalSerializer(goal).data
        })

    @action(detail=True, methods=['delete'])
    def delete_goal(self, request, pk=None):
        try:
            goal = self.get_queryset().get(pk=pk)
        except ReadingGoal.DoesNotExist:
            return Response(
                {"error": "Goal not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        goal.delete()
        return Response(
            {"message": "Goal deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )