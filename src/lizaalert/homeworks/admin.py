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
    list_select_related = ("subscription",)

    def user(self, obj):
        return obj.subscription.user

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(reviewer=request.user)

    def has_change_permission(self, request, obj=None):
        if obj is not None and not request.user.is_superuser:
            return obj.reviewer == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.reviewer = request.user
        super().save_model(request, obj, form, change)
