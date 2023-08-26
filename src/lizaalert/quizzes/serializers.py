from rest_framework import serializers

from .models import Quiz


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = (
            "id",
            "author",
            "title",
            "description",
            "duration_minutes",
            "passing_score",
            "max_attempts",
        )
