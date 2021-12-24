from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators

from reviews.models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('slug', 'name')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(required=True,
                                            slug_field='slug',
                                            queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(required=True,
                                         many=True,
                                         slug_field='slug',
                                         queryset=Genre.objects.all())
    year = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)

    class Meta:
        model = Title
        fields = '__all__'

    @staticmethod
    def validate_year(value):
        if value < 0:
            raise serializers.ValidationError(
                'Год не может быть меньше нуля')
        if value > datetime.today().year:
            raise serializers.ValidationError(
                'Год не может быть больше текущего года')
        return value


class ReadTitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class CurrentTitleDefault:
    """Класс для получения дефолтного произведения из запроса"""
    requires_context = True

    def __call__(self, serializer_field):
        request = serializer_field.context.get('request')
        title = get_object_or_404(
            Title, pk=request.parser_context.get('kwargs').get('title_id'))
        return title

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())
    title = serializers.HiddenField(default=CurrentTitleDefault())

    class Meta:
        model = Review
        fields = '__all__'
        # exclude = ['title']
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['title', 'author']
            )]

    def get_title(self):
        request = self.context.get('request')
        title = get_object_or_404(
            Title, pk=request.parser_context.get('kwargs').get('title_id'))
        return title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        exclude = ('review',)


class UserCreateThroughEmailSerializer(serializers.ModelSerializer):
    username = serializers.SlugField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all(),
            message='Имя пользователя занято')])
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all(),
            message='Такой email уже существует')])

    class Meta:
        model = User
        fields = ('email', 'username')

    @staticmethod
    def validate_username(value):
        if value == 'me':
            raise serializers.ValidationError(
                'Такой username нельзя использовать')
        return value


class UserSerializer(UserCreateThroughEmailSerializer):

    class Meta:
        model = User
        fields = ('username', 'email',
                  'first_name', 'last_name', 'bio', 'role')
