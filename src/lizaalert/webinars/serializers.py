from django.utils import timezone
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from lizaalert.settings.constants import DEFAULT_WEBINAR_LENGTH
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
        """
        Получение статуса прохождения вебинара.

        Если дата-время вебинара + предполагаемая длительность вебинара в минутах, меньше текущего времени,
        то вебинар считается завершенным, иначе - запланированным.
        """
        if (obj.webinar_date + timezone.timedelta(minutes=DEFAULT_WEBINAR_LENGTH)) <= timezone.now():
            return Webinar.Status.FINISHED
        return Webinar.Status.COMING


class ErrorSerializer(serializers.Serializer):
    """Сериализатор ошибки."""

    detail = serializers.CharField()
