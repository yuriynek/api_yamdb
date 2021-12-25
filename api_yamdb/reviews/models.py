import enum

from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_year

SCORES = [(i, i) for i in range(1, 11)]


class Role(enum.Enum):
    user = 'Пользователь'
    moderator = 'Модератор'
    admin = 'Администратор'

    @classmethod
    def choices(cls):
        return tuple((item.name, item.value) for item in cls)


class User(AbstractUser):
    bio = models.TextField('Биография',
                           blank=True,)
    role = models.CharField(choices=Role.choices(), default=Role.user.name, max_length=128)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        # Кастомизируем название таблицы
        # для совместимости с загрузкой данных из CSV в БД
        db_table = 'users'

    @property
    def is_admin(self):
        return self.role == Role.admin.name

    @property
    def is_moderator(self):
        return self.role == Role.moderator.name

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.TextField(max_length=256, verbose_name='Название категории')
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        # Кастомизируем название таблицы
        # для совместимости с загрузкой данных из CSV в БД
        db_table = 'category'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.TextField(verbose_name='Название жанра')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        # Кастомизируем название таблицы
        # для совместимости с загрузкой данных из CSV в БД
        db_table = 'genre'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField(max_length=255,
                            verbose_name='Название произведения')
    year = models.IntegerField(verbose_name='Год выпуска',
                               validators=[validate_year])
    description = models.TextField(max_length=255, verbose_name='Описание')
    genre = models.ManyToManyField(Genre,
                                   through='GenreTitle',
                                   verbose_name='Жанр')
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 verbose_name='Категория',
                                 blank=True,
                                 null=True)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        # Кастомизируем название таблицы
        # для совместимости с загрузкой данных из CSV в БД
        db_table = 'titles'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Жанр-Произведение'
        verbose_name_plural = 'Жанры-Произведения'
        # Кастомизируем название таблицы
        # для совместимости с загрузкой данных из CSV в БД
        db_table = 'genre_title'


class Review(models.Model):
    title = models.ForeignKey(Title,
                              verbose_name='Произведение',
                              on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(User,
                               verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='reviews',
                               db_column='author')
    score = models.IntegerField(verbose_name='Оценка',
                                choices=SCORES)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        # Кастомизируем название таблицы
        # для совместимости с загрузкой данных из CSV в БД
        db_table = 'review'
        constraints = [models.UniqueConstraint(
            fields=['title', 'author'],
            name='unique author review'
        )]

    def __str__(self):
        return self.text[:30]


class Comment(models.Model):
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey('User',
                               verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='comments',
                               db_column='author')
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        # Кастомизируем название таблицы
        # для совместимости с загрузкой данных из CSV в БД
        db_table = 'comments'

    def __str__(self):
        return self.text[:30]
