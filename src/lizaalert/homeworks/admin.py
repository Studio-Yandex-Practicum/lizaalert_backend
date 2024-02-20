from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE

from lizaalert.homeworks.models import Homework


class HomeworkAdminForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = "__all__"
        widgets = {
            "text": TinyMCE(attrs={"cols": 80, "rows": 30}),
        }


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    """Админка домашних заданий."""

    form = HomeworkAdminForm
    list_display = (
        "reviewer",
        "user",
        "status",
        "lesson",
    )
    ordering = ("updated_at",)
    list_select_related = ("subscription",)

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
