from rest_framework import serializers
from .models import ReadingSession
from books.models import ReadingList


class ReadingSessionSerializer(serializers.ModelSerializer):
    duration = serializers.ReadOnlyField()

    class Meta:
        model = ReadingSession
        fields = [
            'id',
            'start_time',
            'end_time',
            'duration',
            'pages_read',
            'note',
            'book',
            'created_at'
        ]
        read_only_fields = ['duration', 'created_at']

    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time.")

        if data['pages_read'] <= 0:
            raise serializers.ValidationError("Pages read must be greater than 0.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        session = ReadingSession.objects.create(user=user, **validated_data)

        # Update ReadingList stats
        reading_list, _ = ReadingList.objects.get_or_create(
            user=user,
            book=session.book
        )

        reading_list.pages_read += session.pages_read
        reading_list.total_hours += session.duration.total_seconds() / 3600
        reading_list.save()

        return session

    def update(self, instance, validated_data):
        old_pages = instance.pages_read
        old_duration = instance.duration.total_seconds() / 3600

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        new_duration = instance.duration.total_seconds() / 3600
        new_pages = instance.pages_read

        reading_list = ReadingList.objects.get(user=instance.user, book=instance.book)

        reading_list.pages_read += (new_pages - old_pages)
        reading_list.total_hours += (new_duration - old_duration)
        reading_list.save()

        return instance