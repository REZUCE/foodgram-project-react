from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Наша собственная проверка прав."""

    def has_object_permission(self, request, view, obj):
        """
        Разрешение на уровне объекта.
        Доступ только пользователю авторам.
        """

        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
