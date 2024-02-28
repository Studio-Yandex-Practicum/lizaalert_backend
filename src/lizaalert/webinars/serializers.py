from rest_framework import serializers

from lizaalert.webinars.models import Webinar


class WebinarSerializer(serializers.ModelSerializer):
    """Сериализатор для вебинара."""

    status = serializers.ChoiceField(source="check_status", choices=Webinar.Status.choices, read_only=True)

    class Meta:
        model = Webinar
        fields = (
            "id",
            "lesson",
            "description",
            "link",
            "recording_link",
            "recording_description",
            "cohort",
            "webinar_date",
            "status",
        )


class ErrorSerializer(serializers.Serializer):
    """Сериализатор ошибки."""

    detail = serializers.CharField()
