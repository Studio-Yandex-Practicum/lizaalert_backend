from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from lizaalert.webinars.models import Webinar


class WebinarSerializer(serializers.ModelSerializer):
    """Сериализатор для вебинара."""

    status = serializers.SerializerMethodField()

    class Meta:
        model = Webinar
        fields = (
            "id",
            "lesson",
            "description",
            "link",
            "recording_link",
            "cohort",
            "webinar_date",
            "status",
        )

    @swagger_serializer_method(serializer_or_field=serializers.ChoiceField(choices=Webinar.Status.choices))
    def get_status(self, obj):
        return obj.check_status


class ErrorSerializer(serializers.Serializer):
    """Сериализатор ошибки."""

    detail = serializers.CharField()
