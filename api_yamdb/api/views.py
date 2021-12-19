from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination

from api_yamdb.api.serializers import TitleSerializer, GenreSerializer, CategorySerializer
from .mixins import CreateByAdminOrReadOnlyModelMixin, AuthorStaffOrReadOnlyModelMixin
from .permissions import IsAdminOrReadOnlyPermission

from reviews.models import Title, Genre, Category
from django_filters.rest_framework import DjangoFilterBackend


class CategoryViewSet(CreateByAdminOrReadOnlyModelMixin):
    """Доступные методы: GET (перечень), POST, DEL.
    На чтение доступ без токена, на добавление/удаление - админу
    Также требуется пагинация и поиск по названию категории"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('slug',)
    search_fields = ('name',)

    pass


class GenreViewSet(CreateByAdminOrReadOnlyModelMixin):
    """Доступные методы: GET (перечень), POST, DEL.
    На чтение доступ без токена, на добавление/удаление - админу
    Также требуется пагинация и поиск по названию жанра"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('slug',)
    search_fields = ('name',)
    pass


class TitleViewSet(viewsets.ModelViewSet):
    """Доступные методы: GET (перечень либо отдельная запись), POST, PATCH, DEL.
    На чтение доступ без токена, на добавление/обновление/удаление - админу
    Также требуется пагинация"""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitOffsetPagination
    filterset_fields = ('name', 'year', 'category__slug', 'genre_slug')


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


# class UserViewSet(...):
#     """Пока что не разбирался - @yurynek"""
#     pass
