from django.contrib import admin

from lizaalert.courses.models import Lesson
from lizaalert.homeworks.models import Homework


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    """Админка домашних заданий."""

    list_display = (
        "reviewer",
        "user",
        "status",
        "lesson",
    )
    ordering = ("updated_at",)
    list_select_related = ("subscription",)

    def user(self, obj):
        return obj.subscription.user

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ограничить в выдаче только уроки типа домашнее задание."""
        if db_field.name == "lesson":
            kwargs["queryset"] = Lesson.objects.filter(lesson_type=Lesson.LessonType.HOMEWORK)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
