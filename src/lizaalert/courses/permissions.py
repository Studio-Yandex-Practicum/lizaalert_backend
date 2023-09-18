from rest_framework import permissions


class IsUserOrReadOnly(permissions.BasePermission):
    """Разрешение только автору выполнять определенное действие."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
