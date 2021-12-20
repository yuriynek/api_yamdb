from rest_framework import serializers
from reviews.models import Category, Genre, Title, Review, Comment, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('slug', 'name')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(required=True, slug_field='slug', queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(required=True, many=True, slug_field='slug', queryset=Genre.objects.all())
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
            return round(sum([item.score for item in queryset])/len(queryset), 2)
        return None


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', default=serializers.CurrentUserDefault(),
                                          queryset=User.objects.all())
    title = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title')
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)

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
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать username "me"!')
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

    def validate_email(self):
        pass