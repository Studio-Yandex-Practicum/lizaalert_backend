from rest_framework.permissions import BasePermission


class IsReviewerOrSuperUser(BasePermission):
    def has_permission(self, request, obj=None):
        """Проверить разрешение на изменение."""
        if obj and not request.user.is_superuser:
            return obj.reviewer == request.user
        return super().has_permission(request, obj)

    def has_object_permission(self, request, view, obj=None):
        """Проверить разрешение на удаление."""
        return False
