from rest_framework import serializers

from .models import Question, Quiz, UserAnswer


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


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = "__all__"
