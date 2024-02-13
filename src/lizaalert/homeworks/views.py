from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lizaalert.courses.models import Course, Lesson, Subscription
from lizaalert.homeworks.exceptions import HomeworkException
from lizaalert.homeworks.models import Homework
from lizaalert.homeworks.serializers import HomeworkSerializer
from lizaalert.users.models import UserRole


class HomeworkViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    Отображение деталей домашней работы.

    Методы:
    - GET: Получение информации домашней работе.
    - POST: При отправлении запроса необходимо передать {'text':'Текст'}
    """

    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        if (
            self.request.user.is_authenticated
            and UserRole.objects.get(user=self.request.user).role == UserRole.Role.VOLUNTEER
        ):
            queryset = Homework.objects.filter(
                lesson=Lesson.objects.get(id=self.kwargs.get("lesson_id")),
                subscription=Subscription.objects.get(
                    user=self.request.user,
                    course=Course.objects.get(chapters=Lesson.objects.get(id=self.kwargs.get("lesson_id")).chapter),
                ),
            ).first()
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        lesson = Lesson.objects.get(id=self.kwargs.get("lesson_id"))
        subscription = Subscription.objects.get(
            user=self.request.user,
            course=Course.objects.get(chapters=lesson.chapter),
        )
        request.data["status"] = Homework.ProgressionStatus.DRAFT
        reviewer = subscription.cohort.teacher
        homework = lesson.homework_set.filter(subscription=subscription).first()
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
