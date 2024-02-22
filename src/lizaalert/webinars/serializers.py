from rest_framework import serializers

from lizaalert.webinars.models import Webinar


class WebinarSerializer(serializers.ModelSerializer):
    """Сериализатор для вебинара."""

    class Meta:
        model = Webinar
        fields = (
            "id",
            "lesson",
            "description",
            "link",
            "cohort",
            "webinar_date",
        )
