from rest_framework import permissions

from lizaalert.courses.utils import update_one_subscription
from lizaalert.settings.constants import get_access_statuses


class IsUserOrReadOnly(permissions.BasePermission):
    """Разрешение только автору выполнять определенное действие."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class CurrentLessonOrProhibited(permissions.BasePermission):
    """Разрешение на просмотр только текущего/пройденных уроков."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_authenticated:
            course = obj.chapter.course
            current_lesson = course.current_lesson(user).first()
            obj = obj.ordered.get(id=obj.id)
            if current_lesson.ordering >= obj.ordering:
                return True
        return False


class EnrolledAndCourseHasStarted(permissions.BasePermission):
    """
    Доступ к урокам курса только для записанных и на курс, который начался.

    access_statuses - статусы пользователся, с которыми можно получить доступ к курсу.
    update_subscriptions - обновляет статусы подписок пользователя.
    """

    message = "Доступ к урокам курса только для подписчиков и на курс, который начался."

    def has_object_permission(self, request, view, obj):
        user = request.user
        course = obj.chapter.course
        update_one_subscription(user, course)
        access_statuses = get_access_statuses()
        if user.is_authenticated:
            try:
                return user.subscriptions.filter(course=course, status__in=access_statuses).exists()
            except Exception:
                return False
        return False
