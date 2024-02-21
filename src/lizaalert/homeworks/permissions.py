from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    def has_change_permission(self, request, obj=None):
        """Проверить разрешение на изменение."""
        if obj and not request.user.is_superuser:
            return obj.reviewer == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Проверить разрешение на удаление."""
        return False
