import rest_framework.exceptions
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
import random
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, filters, mixins, permissions, status
from rest_framework.pagination import LimitOffsetPagination
from django.core.mail import send_mail
from .serializers import TitleSerializer, GenreSerializer, \
    CategorySerializer, ReviewSerializer, CommentSerializer, UserCreateThroughEmailSerializer, UserSerializer, \
    ReadTitleSerializer
from .mixins import CreateByAdminOrReadOnlyModelMixin, AuthorStaffOrReadOnlyModelMixin
from .permissions import IsAdminOrReadOnlyPermission, IsAdminUserPermission
from rest_framework.decorators import api_view, permission_classes
from reviews.models import Title, Genre, Category, Review, User
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TitleFilter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


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
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Category.objects.all()
        slug = self.kwargs.get('slug')
        if slug:
            queryset = queryset.filter(slug=slug)
        return queryset


class GenreViewSet(CreateByAdminOrReadOnlyModelMixin):
    """Доступные методы: GET (перечень), POST, DEL.
    На чтение доступ без токена, на добавление/удаление - админу
    Также требуется пагинация и поиск по названию жанра"""
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('slug',)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Genre.objects.all()
        slug = self.kwargs.get('slug')
        if slug:
            queryset = queryset.filter(slug=slug)
        return queryset


class TitleViewSet(viewsets.ModelViewSet):
    """Доступные методы: GET (перечень либо отдельная запись), POST, PATCH, DEL.
    На чтение доступ без токена, на добавление/обновление/удаление - админу
    Также требуется пагинация"""
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitOffsetPagination
    filterset_class = TitleFilter
    serializer_class = TitleSerializer

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ReadTitleSerializer
        return TitleSerializer


class ReviewViewSet(AuthorStaffOrReadOnlyModelMixin):
    """Методы:
    -GET (перечень либо отдельная запись) - доступ без токена,
    -POST - аутентифицированный юзер,
    -PATCH, DEL - автор, модератор или админ"""
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user,
                        title=title)


class CommentViewSet(AuthorStaffOrReadOnlyModelMixin):
    """Методы:
    -GET (перечень либо отдельная запись) - доступ без токена,
    -POST - аутентифицированный юзер,
    -PATCH, DEL - автор, модератор или админ"""
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user,
                        review=review)


class UserCreateThroughEmailViewSet(viewsets.GenericViewSet,
                                    mixins.CreateModelMixin):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserCreateThroughEmailSerializer

    def perform_create(self, serializer):
        email = self.request.data.get('email')
        confirmation_code = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        message = f'Your confirmation code is: {confirmation_code}'
        send_mail(from_email='yamdb_auth@yamdb.fake',
                  recipient_list=[email],
                  subject='Email confirmation',
                  message=message)
        serializer.save(
            password=make_password(confirmation_code)
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUserPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def get_queryset(self):
        queryset = User.objects.all()
        username = self.kwargs.get('username')
        if not username:
            return queryset
        return queryset.filter(username=username)


@api_view(['PATCH', 'GET'])
def user_own_view(request):
    user = get_object_or_404(User, pk=request.user.pk)

    if request.method != 'PATCH':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    serializer = UserSerializer(user, data=request.data, partial=True)
    role_changed = request.data.get('role')
    change_role_restriction = not (user.role == 'admin' and user.is_superuser)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if role_changed and change_role_restriction:
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


class MyTokenObtainPairView(TokenObtainPairView):

    def post(self, *args, **kwargs):
        if not (self.request.data and self.request.data.get('username')):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if self.request.data.get('username') not in [user.username for user in User.objects.all()]:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return super().post(self.request, *args, **kwargs)
