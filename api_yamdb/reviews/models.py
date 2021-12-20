from django.db import models
from django.contrib.auth.models import AbstractUser

SCORES = [(i, i) for i in range(1, 11)]
USER_ROLES = (('user', 'Пользователь'),
              ('moderator', 'Модератор'),
              ('admin', 'Администратор'))


class User(AbstractUser):
    bio = models.TextField('Биография',
                           blank=True,)
    role = models.CharField(choices=USER_ROLES, default='user', max_length=128)

    class Meta:
        db_table = 'users'


class Category(models.Model):
    name = models.TextField(max_length=256, verbose_name='Название категории')
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        db_table = 'category'


class Genre(models.Model):
    name = models.TextField(verbose_name='Название жанра')
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = 'genre'


class Title(models.Model):
    name = models.TextField(max_length=255,
                            verbose_name='Название произведения')
    year = models.IntegerField(verbose_name='Год выпуска')
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
        db_table = 'titles'


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
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
        db_table = 'review'
        constraints = [models.UniqueConstraint(
            fields=['title', 'author'],
            name='unique author review'
        )]


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
        db_table = 'comments'
