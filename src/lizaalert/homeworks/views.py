from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from lizaalert.courses.models import Subscription
from lizaalert.homeworks.exceptions import HomeworkException
from lizaalert.homeworks.models import Homework
from lizaalert.homeworks.serializers import HomeworkSerializer


class HomeworkViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Отображение деталей домашней работы.

    Методы:
    - GET: Получение информации домашней работе.
    - POST: При отправлении запроса необходимо передать {'text':'Текст сохранен', 'status':0} --> сохранено
    - POST: При отправлении запроса необходимо передать {'text':'Текст отправлен', 'status':1} --> отправлено
    """

    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "lesson_id"

    def perform_create(self, serializer):
        lesson_id = self.kwargs.get("lesson_id")
        subscription = get_object_or_404(Subscription, user=self.request.user, course__chapters__lessons__id=lesson_id)
        homework, created = Homework.objects.get_or_create(
            lesson_id=lesson_id, subscription=subscription, defaults={"reviewer": subscription.cohort.teacher}
        )
        if not created:
            for attr, value in serializer.validated_data.items():
                setattr(homework, attr, value)
            homework.save()
        serializer.instance = homework
        return super().perform_create(serializer)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly." % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        try:
            obj = get_object_or_404(queryset, **filter_kwargs)
        except Http404 as e:
            HomeworkException.default_detail = ["У пользователя пока нет домашней работы", e]
            raise HomeworkException
        self.check_object_permissions(self.request, obj)
        return obj
