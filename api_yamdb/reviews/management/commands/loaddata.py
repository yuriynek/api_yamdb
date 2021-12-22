import csv
import os

from django.core.management.base import BaseCommand

from api_yamdb import settings
from reviews import models

CSV_DATA_PATH = os.path.join(settings.STATICFILES_DIRS[0], 'data/')

FILE_MODEL_DICT = {
    'category.csv': models.Category,
    'comments.csv': models.Comment,
    'genre.csv': models.Genre,
    'genre_title.csv': models.GenreTitle,
    'review.csv': models.Review,
    'titles.csv': models.Title,
    'users.csv': models.User
}

TABLES_FOREIGN_KEYS = {
    'comments.csv': {
        'author': lambda pk: models.User.objects.get(pk=pk),
        'review': lambda pk: models.Review.objects.get(pk=pk)},
    'genre_title.csv': {
        'genre': lambda pk: models.GenreTitle.objects.get(genre_id=pk),
        'title': lambda pk: models.GenreTitle.objects.get(title_id=pk)},
    'review.csv': {
        'author': lambda pk: models.User.objects.get(pk=pk),
        'title': lambda pk: models.Title.objects.get(pk=pk)},
    'titles.csv': {
        'category': lambda pk: models.Category.objects.get(pk=pk)},
}

LOADING_ORDER = ['category.csv', 'genre.csv', 'titles.csv', 'genre_title.csv',
                 'users.csv', 'review.csv', 'comments.csv']


class Command(BaseCommand):
    help = 'Load data from .csv file into database'

    def handle(self, *args, **options):
        """Загружаем файлы из csv в БД."""
        files = LOADING_ORDER

        #  Проходим каждый файл
        for file in files:
            try:
                with open('/'.join([CSV_DATA_PATH, file]),
                          encoding='UTF-8', newline='') as csv_file:
                    # Считываем данные из csv в виде словаря
                    reader = csv.DictReader(csv_file)
                    # Формируем данные.
                    # Если поле является ForeignKey,
                    # то берем из связанной модели конкретный экземпляр
                    # с помощью TABLES_FOREIGN_KEYS
                    for row in reader:
                        data = {}
                        for k, v in row.items():
                            if (TABLES_FOREIGN_KEYS.get(file)
                                    and k in TABLES_FOREIGN_KEYS.get(file)):
                                data[k] = TABLES_FOREIGN_KEYS[file][k](int(v))
                            else:
                                data[k] = v
                        # записываем подготовленные данные в БД
                        FILE_MODEL_DICT[file].objects.create(**data)
            except Exception as error:
                self.stdout.write('ПРОИЗОШЛА ОШИБКА:')
                self.stdout.write(error)
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'...Данные успешно загружены из файла {file}...'))
