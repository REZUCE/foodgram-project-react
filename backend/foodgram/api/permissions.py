from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Наша собственная проверка прав."""

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        """
        Разрешение на уровне объекта. Только author или admin.
        Срабатывает если has_permission вернул True.
        """

        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
