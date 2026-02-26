from rest_framework import serializers
from .models import ReadingGoal


class ReadingGoalSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField(read_only=True)
    days_since_created = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReadingGoal
        fields = [
            'id',
            'goal_type',
            'target_value',
            'is_completed',
            'created_at',
            'updated_at',
            'progress',
            'days_since_created'
        ]
        read_only_fields = ['is_completed', 'created_at', 'updated_at']

    def get_progress(self, obj):
        return {"available": True, "endpoint": f"/api/goals/{obj.id}/progress/"}

    def get_days_since_created(self, obj):
        from django.utils import timezone
        delta = timezone.now().date() - obj.created_at.date()
        return delta.days

    def validate(self, data):
        if data['target_value'] <= 0:
            raise serializers.ValidationError(
                {"target_value": "Target value must be greater than 0."}
            )

        if not self.instance:
            user = self.context['request'].user
            existing_goal = ReadingGoal.objects.filter(
                user=user,
                goal_type=data['goal_type'],
                is_completed=False
            ).first()

            if existing_goal:
                raise serializers.ValidationError(
                    {
                        "goal_type": f"You already have an active {data['goal_type']} goal. Complete it first or delete it."}
                )

        return data

    def create(self, validated_data):
        """Create goal with current user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)