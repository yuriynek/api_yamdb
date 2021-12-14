from django.db import models

SCORES = [i for i in range(1, 11)]


class Review(models.Model):
    title = models.ForeignKey('Title',
                              verbose_name='Произведение',
                              on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey('User',
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
