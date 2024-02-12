from django.core.exceptions import ObjectDoesNotExist


from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import APIException, ValidationError


from lizaalert.courses.models import Lesson, Subscription, LessonProgressStatus, Course
from lizaalert.homeworks.models import Homework
from lizaalert.homeworks.serializers import (
    HomeworkDetailSerializer,
    HomeworkSerializer,

)
#from lizaalert.users.models import Level

class HomeworkException(APIException):
    """Базовый класс для исключений, связанных с квизами."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Некорректный запрос"


class HomeworkViewSet(generics.ListAPIView):
    """
    Класс дял отображение всех домашних работ одного преподавателя.

    Методы:
    - GET: Получение информации о квизе и его вопросах.
    """
    serializer_class = HomeworkSerializer

    def get_queryset(self):
        lesson = self.request.query_params.get('lesson')
        if lesson:
            return Homework.objects.filter(reviewer=self.request.user, lesson=lesson)
        return Homework.objects.filter(reviewer=self.request.user)


class HomeworkDetailViewSet(generics.RetrieveAPIView, generics.CreateAPIView):
    """
    Отображение деталей домашней работы.

    Методы:
    - GET: Получение информации домашней работе.
    - POST:
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
        lesson = request.data.get('lesson')
        if lesson:
            try:
                homework = Homework.objects.get(id=request.data.get('id'))
                homework.text = request.data.get('text')
                return Response(request.data, status=status.HTTP_201_CREATED)
            except ObjectDoesNotExist as e:
                HomeworkException.default_code = e
                raise HomeworkException

        lesson_id = self.kwargs.get('lesson_id')
        request.data['status'] = Homework.ProgressionStatus.SUBMITTED
        request.data['subscription'] = Subscription.objects.get(user=self.request.user, course=Course.objects.get(
            chapters=Lesson.objects.get(id=self.kwargs.get('lesson_id')).chapter)).pk
        request.data['lesson'] = Lesson.objects.get(id=lesson_id).pk
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(
            status=Homework.ProgressionStatus.SUBMITTED,
        )
