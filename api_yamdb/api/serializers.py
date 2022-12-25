import re

from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from reviews.models import Title, Category, Genre, User, Comment, Review


class SendCodeSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[],
    )
    email = serializers.EmailField(
        max_length=254,
    )

    def validate(self, data):
        errors = {}

        if not data.get("username", False):
            errors["username"] = "Это поле обязательно"
        if not data.get("email", False):
            errors["email"] = "Это поле обязательно"
        user = data.get("username", False)
        if user.lower() == "me":
            raise serializers.ValidationError("Username 'me' is not valid")
        if re.search(r'^[\w.@+-]+$', user) is None:
            raise ValidationError(
                (f'Не допустимые символы <{user}> в нике.'),
                params={'value': user},
            )
        if errors:
            raise serializers.ValidationError(errors)

        if User.objects.filter(email=data["email"]):
            user = User.objects.get(email=data["email"])
            if user.username != data["username"]:
                raise serializers.ValidationError(
                    {"email": "Данный email уже зарегистрирован"}
                )
        elif User.objects.filter(username=data["username"]):
            user = User.objects.get(username=data["username"])
            if user.email != data["email"]:
                raise serializers.ValidationError(
                    {"email": "Данный email уже зарегистрирован"}
                )
        return data


class CheckConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=200
    )
    confirmation_code = serializers.CharField(
        required=True
    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')


class IsNotAdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=50, min_length=None, allow_blank=False)

    def validate_slug(self, value):
        if Category.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                'Категория с таким slug уже существует!'
            )
        return value

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
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title


class TitleReWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        if request.method == 'POST':
            if Review.objects.filter(
                    title=get_object_or_404(Title, pk=title_id),
                    author=request.user).exists():
                raise ValidationError(
                    'Error'
                )
        return data

    class Meta:
        model = Review
        fields = '__all__'
