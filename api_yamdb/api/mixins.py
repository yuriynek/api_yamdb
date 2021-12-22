from rest_framework import mixins, viewsets

from .permissions import (IsAdminOrReadOnlyPermission,
                          IsAuthorOrStaffOrReadOnlyPermission)


class CreateByAdminOrReadOnlyModelMixin(mixins.CreateModelMixin,
                                        mixins.ListModelMixin,
                                        mixins.DestroyModelMixin,
                                        viewsets.GenericViewSet):
    """Миксин-вьюсет для получения списка объектов
    либо создания/удаления объекта админом"""
    permission_classes = (IsAdminOrReadOnlyPermission,)


class AuthorStaffOrReadOnlyModelMixin(viewsets.ModelViewSet):
    """Миксин-вьюсет для чтения любым пользователем,
    создания записей авторизованным ользователем,
    изменения/удаления автором/модератором/админом"""
    permission_classes = (IsAuthorOrStaffOrReadOnlyPermission,)
