from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import User, Category, Genre, Title, Comment, Review
from reviews.validators import validate_username, validate_year


class SendCodeSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True,
        validators=[validate_username],
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH,
        required=True
    )


class CheckConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=[validate_username],
    )
    confirmation_code = serializers.CharField(
        required=True,
        max_length=settings.CONFIRMCODE_MAX_LENGTH
    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class UserMeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id', )
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, required=True)
    genre = GenreSerializer(many=True, required=False)
    rating = serializers.IntegerField()
    year = serializers.IntegerField(
        validators=[validate_year],
    )

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        model = Title
        read_only_fields = fields


class TitleReWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', many=False, queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        required=False,
        queryset=Genre.objects.all()
    )

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(
                title=get_object_or_404(Title, pk=title_id),
                author=request.user).exists():
            raise ValidationError(
                'Не найдено произведение или отзыв'
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
