from rest_framework import serializers

from lizaalert.homeworks.models import Homework


class HomeworkSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для домашних работ."""

    status = serializers.ChoiceField(choices=Homework.ProgressionStatus)
    reviewer = serializers.StringRelatedField(read_only=True)
    subscription = serializers.PrimaryKeyRelatedField(read_only=True)
    lesson = serializers.PrimaryKeyRelatedField(read_only=True)
    required = serializers.BooleanField(read_only=True)

    class Meta:
        model = Homework
        fields = (
            "id",
            "reviewer",
            "status",
            "lesson",
            "text",
            "subscription",
            "required",
        )


class EmptyHomeworkSerializer(serializers.Serializer):
    """Сериалайзер класс для домашних работ."""

    status = serializers.CharField(default=Homework.ProgressionStatus.DRAFT, initial=Homework.ProgressionStatus.DRAFT)
    text = serializers.CharField(default="", initial="")
