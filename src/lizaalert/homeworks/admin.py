from django.contrib import admin

from lizaalert.homeworks.models import Homework


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    """Админка домашней работы."""

    model = Homework
    extra = 1
    list_display = (
        "id",
        "reviewer",
        "status",
        "lesson",
        "text",
        "subscription",
        "required",
    )
    list_select_related = ("lesson",)
    ordering = ("-updated_at",)
