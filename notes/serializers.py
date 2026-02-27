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
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        if self.partial:
            if 'content' in data and (not data['content'] or not data['content'].strip()):
                raise serializers.ValidationError("Note content cannot be empty.")

            book = data.get('book')
            session = data.get('session')

            if book and session:
                raise serializers.ValidationError("Note cannot belong to both.")

            instance = getattr(self, 'instance', None)
            if instance:
                current_book = book if book is not None else instance.book_id
                current_session = session if session is not None else instance.session_id

                if not current_book and not current_session:
                    raise serializers.ValidationError("Note must belong to a book or a session.")
        else:
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
