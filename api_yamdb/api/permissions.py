from rest_framework import permissions


class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    message = 'Права на изменение данного контента принадлежат администратору'

    def has_object_permission(self, request, view, obj):
        """Проверка. Если запрос только на чтение, то разрешаем его.
        Если на изменение - проверяем, является ли пользователь админом"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'admin'


class IsAuthorOrStaffOrReadOnlyPermission(permissions.BasePermission):
    message = ('Права на изменение данного контента принадлежат '
               'администраторам, модераторам либо авторам записей')

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Проверка. Если запрос только на чтение, то разрешаем его.
        Если пользователь авторизован - разрешает создание записи
        Если запрос на изменение - проверяем, является ли пользователь админом/модератором/автором"""
        return any([request.user.role == 'admin',
                    request.user.role == 'moderator',
                    obj.author == request.user
                    ])
