from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE

from lizaalert.courses.models import Lesson
from lizaalert.homeworks.models import Homework
from lizaalert.settings.admin_setup import BaseAdmin


class HomeworkAdminForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ("reviewer", "status", "lesson", "text", "subscription", "required")
        widgets = {
            "text": TinyMCE(attrs={"cols": 80, "rows": 10}),
        }


@admin.register(Homework)
class HomeworkAdmin(BaseAdmin):
    """Админка домашних заданий."""

    form = HomeworkAdminForm
    list_display = (
        "id",
        "reviewer",
        "user",
        "status",
        "lesson",
    )
    ordering = ("updated_at",)
    list_select_related = ("subscription__user",)

    def user(self, obj):
        """Получить пользователя, связанного с подпиской на задание."""
        return obj.subscription.user

    def get_queryset(self, request):
        """
        Получить запрос к базе данных.

        Если пользователь имеет статус суперпользователя, то он видит все домашние задания.
        Если пользователь обычный администратор, то он видит только те домашние задания,
         ревьюером которых является.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(reviewer=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ограничить в выдаче только уроки типа домашнее задание."""
        if db_field.name == "lesson":
            kwargs["queryset"] = Lesson.objects.filter(lesson_type=Lesson.LessonType.HOMEWORK)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
