from rest_framework import serializers
from .models import Goal, GoalBook


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'target_value', 'progress', 'deadline', 'user']


class GoalBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalBook
        fields = ['id', 'goal', 'book']
