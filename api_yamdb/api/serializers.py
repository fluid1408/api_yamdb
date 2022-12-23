import re
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from django.contrib.auth import authenticate

from reviews.models import Title, Category, Genre, User, Comment, Review
from rest_framework.generics import get_object_or_404


class SendCodeSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
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
        if errors:
            raise serializers.ValidationError(errors)
        return data


class CheckConfirmationCodeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=200)
    confirmation_code = serializers.CharField()


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


class TitleSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Genre

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
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError()
        return data

    class Meta:
        model = Review
        fields = 'all'

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
        fields = 'all'
