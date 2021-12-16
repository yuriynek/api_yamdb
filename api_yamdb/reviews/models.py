from django.db import models
from django.contrib.auth.models import AbstractUser

SCORES = [i for i in range(1, 11)]


class User(AbstractUser):
<<<<<<< HEAD
    bio = models.TextField('Биография',
                           blank=True,)
    role = models.CharField(choices=...)


class Category(models.Model):
    name = models.TextField(max_length=256, verbose_name='Название категории')
    slug = models.SlugField(max_length=50, unique=True)


class Genre(models.Model):
    name = models.TextField(verbose_name='Название жанра')
=======
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(choices=...)



class Category(models.Model):
    slug = models.SlugField(unique=True)



class Genre(models.Model):
>>>>>>> bd18dedd057040cf06587f3753b41c0d524e64a0
    slug = models.SlugField(unique=True)


class Title(models.Model):
<<<<<<< HEAD
    name = models.TextField(max_length=255,
                            verbose_name='Название произведения')
    year = models.IntegerField(verbose_name='Год выпуска')
    description = models.TextField(max_length=255, verbose_name='Описание')
    genre = models.ForeignKey(Genre,
                              on_delete=models.SET_NULL,
                              verbose_name='Жанр',
                              blank=True,
                              null=True)
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 verbose_name='Категория',
                                 blank=True,
                                 null=True)
=======
    name = models.TextField(max_length=255, verbose_name="name")
    year = models.IntegerField()
    category = models.ForeignKey(Category, verbose_name="Category")
    genre = models.ForeignKey(Genre,
                              on_delete=models.SET_NULL,

                              )

>>>>>>> bd18dedd057040cf06587f3753b41c0d524e64a0


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


class Comment(models.Model):
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey('User',
                               verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='reviews',
                               db_column='author')
    pub_date = models.DateTimeField(auto_now_add=True)
