from rest_framework import serializers

from lizaalert.quizzes.models import Question, Quiz, UserAnswer


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "title",
            "answers",
            "question_type",
        )


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = (
            "id",
            "title",
            "description",
            "status",
            "passing_score",
            "retries",
            "in_progress",
            "deadline",
        )


class QuizWithQuestionsSerializer(QuizSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = QuizSerializer.Meta.fields + ("questions",)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["questions"] = QuestionSerializer(instance.question_set.all(), many=True).data
        return representation


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = "__all__"
