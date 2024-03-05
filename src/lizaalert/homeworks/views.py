from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, response, status, viewsets
from rest_framework.permissions import IsAuthenticated

from lizaalert.courses.models import Subscription
from lizaalert.homeworks.models import Homework
from lizaalert.homeworks.serializers import EmptyHomeworkSerializer, HomeworkSerializer


class HomeworkViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Отображение деталей домашней работы.

    Методы:
    - GET: Получение информации домашней работе.
    - POST: При отправлении запроса необходимо передать {'text':'Текст сохранен', 'status':draft} --> сохранено
    - POST: При отправлении запроса необходимо передать {'text':'Текст отправлен', 'status':submitted} --> отправлено
    """

    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "lesson_id"

    def perform_create(self, serializer):
        lesson_id = self.kwargs.get("lesson_id")
        subscription = get_object_or_404(Subscription, user=self.request.user, course__chapters__lessons__id=lesson_id)
        try:
            reviewer = subscription.cohort.teacher
        except AttributeError:
            reviewer = None
        homework, created = Homework.objects.get_or_create(
            lesson_id=lesson_id, subscription=subscription, defaults={"reviewer": reviewer}
        )
        homework.status = serializer.validated_data.get("status")
        homework.text = serializer.validated_data.get("text")
        homework.save()
        serializer.instance = homework

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: HomeworkSerializer,
            status.HTTP_404_NOT_FOUND: EmptyHomeworkSerializer,
        }
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = get_object_or_404(
                Homework,
                lesson_id=kwargs.get("lesson_id"),
                subscription__user=request.user,
                subscription__course__chapters__lessons=kwargs.get("lesson_id"),
            )
            serializer = self.get_serializer(instance)
        except Http404:
            serializer = EmptyHomeworkSerializer()
            return response.Response(serializer.data, status=status.HTTP_404_NOT_FOUND)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
