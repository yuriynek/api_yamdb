from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .mixins import (AuthorStaffOrReadOnlyModelMixin,
                     CreateByAdminOrReadOnlyModelMixin)
from .permissions import IsAdminOrReadOnlyPermission, IsAdminUserPermission
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReadTitleSerializer,
                          ReviewSerializer, TitleSerializer,
                          UserCreateThroughEmailSerializer, UserSerializer)


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
    queryset = Category.objects.all()


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
    queryset = Genre.objects.all()


class TitleViewSet(viewsets.ModelViewSet):
    """Доступные методы: GET (перечень либо отдельная запись), POST, PATCH, DEL.
    На чтение доступ без токена, на добавление/обновление/удаление - админу
    Также требуется пагинация"""
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
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
                                    mixins.CreateModelMixin,
                                    PasswordResetView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserCreateThroughEmailSerializer

    def perform_create(self, serializer):
        # после валидации сериализатора сохраняем нового юзера
        email = self.request.data.get('email')
        user = serializer.save()
        # генерируем юзеру шестизначный код подтверждения с помощью токена
        confirmation_code = self.token_generator.make_token(user=user)[-7:-1]
        # шифруем и сохраняем в БД для конкретного пользователя
        user.password = make_password(confirmation_code)
        user.save()
        message = f'Your confirmation code is: {confirmation_code}'
        send_mail(from_email=self.from_email,
                  recipient_list=[email],
                  subject='Email confirmation',
                  message=message)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminUserPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    queryset = User.objects.all()
    filterset_fields = ('slug',)


@api_view(['PATCH', 'GET'])
def user_own_view(request):
    user = get_object_or_404(User, pk=request.user.pk)

    if request.method != 'PATCH':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    serializer = UserSerializer(user, data=request.data, partial=True)
    role_changed = request.data.get('role')
    change_role_restriction = not (user.is_admin and user.is_superuser)
    serializer.is_valid(raise_exception=True)

    if role_changed and change_role_restriction:
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


class MyTokenObtainPairView(TokenObtainPairView):

    def post(self, *args, **kwargs):
        if not (self.request.data and self.request.data.get('username')):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(User, username=self.request.data.get('username'))
        return super().post(self.request, *args, **kwargs)
