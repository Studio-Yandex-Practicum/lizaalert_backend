from django.contrib import admin

from lizaalert.homeworks.models import Homework


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    """Админка домашних заданий."""

    model = (Homework,)
    list_display = (
        "reviewer",
        "user",
        "status",
        "lesson",
    )
    ordering = ("lesson",)
    list_select_related = ("lesson",)

    @admin.display(empty_value="")
    def user(self, obj):
        return obj.subscription.user
