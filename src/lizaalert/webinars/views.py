from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from lizaalert.webinars.exceptions import NoSuitableWebinar
from lizaalert.webinars.models import Webinar
from lizaalert.webinars.serializers import WebinarSerializer


class WebinarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Отображение вебинара.

    Метод:
    GET - получение вебинара.
    Queryset - нам нужен ближайший вебинар для этого урока для этой когорты.
    """

    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = WebinarSerializer
    lookup_field = "lesson_id"

    def get_queryset(self):
        lesson = self.kwargs.get("lesson_id")
        user = self.request.user
        return Webinar.objects.filter(
            lesson_id=lesson, cohort__subscriptions__user_id=user, cohort__course__chapters__lessons=lesson
        ).order_by("webinar_date")

    def get_object(self):
        queryset = self.get_queryset()
        if obj := queryset.first():
            return obj
        raise NoSuitableWebinar()
