import re
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from django.contrib.auth import authenticate

from reviews.models import Title, Category, Genre, User


class SendCodeSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
    )
    email = serializers.EmailField(
        max_length=254,
    )

    def validate_username(self, value):
        if value.lower() == "me":
            raise serializers.ValidationError("Username 'me' is not valid")
        if re.search(r'^[\w.@+-]+$', value) is None:
            raise ValidationError(
                (f'Не допустимые символы <{value}> в нике.'),
                params={'value': value},
            )
        return value

    class Meta:
        fields = ("username", "email")
        model = User


class CheckConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('first_name', 'last_name', 'username', 'email', 'bio', 'role')
        model = User
        extra_kwargs = {
            'password': {'required': False},
            'email': {'required': True}
        }


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
