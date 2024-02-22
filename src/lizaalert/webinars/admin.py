from django.contrib import admin

from lizaalert.courses.models import Lesson
from lizaalert.webinars.models import Webinar


@admin.register(Webinar)
class Webinar(admin.ModelAdmin):
    """
    Админка домашних заданий.

    При создании вебинара, можно выбрать только уроки типа ВЕБИНАР.
    """

    list_display = (
        "lesson",
        "cohort",
        "webinar_date",
    )
    ordering = ("updated_at",)
    list_select_related = (
        "cohort",
        "lesson",
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ограничить в выдаче только уроки типа вебинар."""
        if db_field.name == "lesson":
            kwargs["queryset"] = Lesson.objects.filter(lesson_type=Lesson.LessonType.WEBINAR)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
