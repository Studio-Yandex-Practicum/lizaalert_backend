import json

from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers

from lizaalert.quizzes.models import Question, Quiz, UserAnswer
from lizaalert.quizzes.validators import ValidateIUserAnswersModel


class ContentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()


class QuestionSerializer(serializers.ModelSerializer):
    content = ContentSerializer(many=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "title",
            "content",
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
        representation["questions"] = QuestionSerializer(instance.questions.all(), many=True).data
        return representation


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = "__all__"

    def validate(self, data):
        try:
            answers_data = {
                "answers": data.get("answers"),
                "result": data.get("result"),
            }
            validated_data = ValidateIUserAnswersModel(**answers_data)
            data["answers"] = json.loads(validated_data.json())["answers"]
            return data
        except PydanticValidationError as e:
            raise serializers.ValidationError(e.errors())

    def create(self, validated_data):
        user_answer = UserAnswer(**validated_data)
        user_answer.save()
        return user_answer
