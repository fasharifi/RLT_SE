from rest_framework import serializers
from .models import ReadingGoal


class ReadingGoalSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReadingGoal
        fields = [
            'id',
            'goal_type',
            'target_value',
            'current_value',
            'is_completed',
            'created_at'
        ]
        read_only_fields = ['current_value', 'is_completed', 'created_at']

    def validate(self, data):
        if data['target_value'] <= 0:
            raise serializers.ValidationError(
                "Target value must be greater than 0."
            )

        if data['goal_type'] not in ['pages', 'books', 'time']:
            raise serializers.ValidationError(
                "Invalid goal type."
            )

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        return ReadingGoal.objects.create(user=user, **validated_data)