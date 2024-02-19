from django.contrib import admin

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
    list_select_related = (
        "subscription",
        # "user",
    )

    def user(self, obj):
        """Получить пользователя, связанного с подпиской на задание."""
        return obj.subscription.user

    def get_queryset(self, request):
        """Получить запрос к базе данных."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(reviewer=request.user)

    def has_change_permission(self, request, obj=None):
        """Проверить разрешение на изменение."""
        if obj and not request.user.is_superuser:
            return obj.reviewer == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Проверить разрешение на удаление."""
        return False

    def save_model(self, request, obj, form, change):
        """Сохранить модель."""
        if not change:
            obj.reviewer = request.user
        super().save_model(request, obj, form, change)
