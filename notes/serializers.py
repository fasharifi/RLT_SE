from rest_framework import serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'id',
            'content',
            'book',
            'session',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        if not data.get('content') or not data['content'].strip():
            raise serializers.ValidationError("Note content cannot be empty.")

        book = data.get('book')
        session = data.get('session')

        if not book and not session:
            raise serializers.ValidationError("Note must belong to a book or a session.")

        if book and session:
            raise serializers.ValidationError("Note cannot belong to both.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        return Note.objects.create(user=user, **validated_data)