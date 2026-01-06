from rest_framework import serializers
from .models import StudySession


class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = ['id', 'start_time', 'end_time', 'pages_read', 'book', 'user']
