from rest_framework import permissions


class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    """Проверка. Если запрос только на чтение, то разрешаем его.
    Если на изменение - проверяем, является ли пользователь админом"""
    message = 'Права на изменение данного контента принадлежат администратору'

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and (request.user.role == 'admin'
                     or request.user.is_superuser))


class IsAuthorOrStaffOrReadOnlyPermission(permissions.BasePermission):
    """Проверка. Если запрос только на чтение, то разрешаем его.
    Если пользователь авторизован - разрешает создание записи
    Если запрос на изменение - проверяем, является ли пользователь
    админом/модератором/автором"""
    message = ('Права на изменение данного контента принадлежат '
               'администраторам, модераторам либо авторам записей')

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return any([obj.author == request.user,
                    request.user.role == 'admin',
                    request.user.role == 'moderator'])


class IsAdminUserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.role == 'admin'
                     or request.user.is_superuser))
