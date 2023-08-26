from rest_framework import serializers

from .models import Question, Quiz


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


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "question_type",
            "quiz",
            "title",
            "answers",
            "order_number",
        )
