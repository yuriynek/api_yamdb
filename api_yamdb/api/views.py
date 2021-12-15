from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .mixins import CreateByAdminOrReadOnlyModelMixin, AuthorStaffOrReadOnlyModelMixin
from permissions import IsAdminOrReadOnlyPermission


class CategoryViewSet(CreateByAdminOrReadOnlyModelMixin):
    """Доступные методы: GET (перечень), POST, DEL.
    На чтение доступ без токена, на добавление/удаление - админу
    Также требуется пагинация и поиск по названию категории"""
    pass


class GenreViewSet(CreateByAdminOrReadOnlyModelMixin):
    """Доступные методы: GET (перечень), POST, DEL.
    На чтение доступ без токена, на добавление/удаление - админу
    Также требуется пагинация и поиск по названию жанра"""
    pass


class TitleViewSet(ModelViewSet):
    """Доступные методы: GET (перечень либо отдельная запись), POST, PATCH, DEL.
    На чтение доступ без токена, на добавление/обновление/удаление - админу
    Также требуется пагинация"""
    permission_classes = (IsAdminOrReadOnlyPermission,)
    pass


class ReviewViewSet(AuthorStaffOrReadOnlyModelMixin):
    """Методы:
    -GET (перечень либо отдельная запись) - доступ без токена,
    -POST - аутентифицированный юзер,
    -PATCH, DEL - автор, модератор или админ
    Мб имет смысл разбить на два вьюсета по правам доступа?"""
    def get_queryset(self):
        title = ...  # get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()


class CommentViewSet(AuthorStaffOrReadOnlyModelMixin):
    """Методы:
    -GET (перечень либо отдельная запись) - доступ без токена,
    -POST - аутентифицированный юзер,
    -PATCH, DEL - автор, модератор или админ"""
    pass


class UserViewSet(...):
    """Пока что не разбирался - @yurynek"""
    pass
