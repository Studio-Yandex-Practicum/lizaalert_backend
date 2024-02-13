from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from lizaalert.courses.models import Course, Lesson, Subscription
from lizaalert.homeworks.models import Homework
from lizaalert.homeworks.serializers import HomeworkSerializer


class HomeworkException(APIException):
    """Базовый класс для исключений, связанных с квизами."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Некорректный запрос"


class HomeworkViewSet(generics.ListAPIView):
    """
    Класс для отображения всех домашних работ одного преподавателя.

    Методы:
    - GET: Получение информации о домашних работах для преподавателя.
    """

    serializer_class = HomeworkSerializer

    def get_queryset(self):
        lesson = self.request.query_params.get("lesson")
        if lesson:
            return Homework.objects.filter(reviewer=self.request.user, lesson=lesson)
        return Homework.objects.filter(reviewer=self.request.user)


class HomeworkDetailViewSet(generics.RetrieveAPIView, generics.CreateAPIView):
    """
    Отображение деталей домашней работы.

    Методы:
    - GET: Получение информации домашней работе.
    - POST: При отправлении запроса необходимо передать {'text':'Текст'}
    """

    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer

    def get_object(self):
        lesson = get_object_or_404(Lesson, id=self.kwargs.get("lesson_id"))
        try:
            homework = lesson.homework_set.first()
            return homework
        except ObjectDoesNotExist as e:
            HomeworkException.default_detail = e
            raise HomeworkException

    def create(self, request, *args, **kwargs):
        lesson = Lesson.objects.get(id=self.kwargs.get("lesson_id"))
        homework = lesson.homework_set.first()
        subscription = Subscription.objects.get(
            user=self.request.user,
            course=Course.objects.get(chapters=lesson.chapter),
        )
        reviewer = subscription.cohort.teacher
        if homework:
            try:
                serializer = self.get_serializer(homework, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(lesson=lesson, status=Homework.ProgressionStatus.SUBMITTED, reviewer=reviewer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            except ObjectDoesNotExist as e:
                HomeworkException.default_code = e
                raise HomeworkException
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            lesson=lesson, status=Homework.ProgressionStatus.SUBMITTED, subscription=subscription, reviewer=reviewer
        )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
