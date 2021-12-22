from django.shortcuts import get_object_or_404
from rest_framework import serializers

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
        fields = ('id', 'category', 'genre', 'name', 'year',
                  'description')


class ReadTitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(required=True)
    genre = GenreSerializer(many=True, required=True)
    rating = serializers.SerializerMethodField()
    year = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)

    class Meta:
        model = Title
        fields = ('id', 'category', 'genre', 'name', 'year', 'rating',
                  'description')

    @staticmethod
    def get_rating(obj):
        queryset = obj.reviews.all()
        if queryset:
            return round(sum(
                [item.score for item in queryset]) / len(queryset), 2)
        return None


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Review
        exclude = ['title']

    def validate(self, data):
        """Валидация уникального сочетания полей [title, author]
        Через UniqueTogetherValidator выдает ошибку БД IntegrityError"""
        request = self.context.get('request')
        if request.method != 'POST':
            return data
        user = request.user
        title = get_object_or_404(
            Title, pk=request.parser_context.get('kwargs').get('title_id'))
        if Review.objects.filter(author=user, title=title).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на данное произведение!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        exclude = ('review',)


class UserCreateThroughEmailSerializer(serializers.ModelSerializer):
    username = serializers.SlugField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username')

    @staticmethod
    def validate_username(value):
        usernames = [user.username for user in User.objects.all()]
        if value in usernames:
            raise serializers.ValidationError(
                'Такой username уже существует!')
        if value == 'me':
            raise serializers.ValidationError(
                'Такой username нельзя использовать')
        return value

    @staticmethod
    def validate_email(value):
        emails = [user.email for user in User.objects.all()]
        if value in emails:
            raise serializers.ValidationError(
                'Такой email уже существует')
        return value


class UserSerializer(serializers.ModelSerializer):
    username = serializers.SlugField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email',
                  'first_name', 'last_name', 'bio', 'role')

    @staticmethod
    def validate_email(value):
        emails = [user.email for user in User.objects.all()]
        if value in emails:
            raise serializers.ValidationError(
                'Такой email уже существует')
        return value

    @staticmethod
    def validate_username(value):
        usernames = [user.username for user in User.objects.all()]
        if value in usernames:
            raise serializers.ValidationError(
                'Такой username уже существует!')
        if value == 'me':
            raise serializers.ValidationError(
                'Такой username нельзя использовать')
        return value
