from datetime import datetime, timedelta
import jwt

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
)
from django.core.validators import RegexValidator


from .validators import validate_username


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.model(email=email, is_staff=True, is_superuser=True, **kwargs)
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

    ROLES = (
        (ADMIN, "Администратор"),
        (MODERATOR, "Модератор"),
        (USER, "Пользователь"),
    )
    username = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        validators=[
            validate_username,
        ],
        verbose_name="Ник пользователя",
    )
    email = models.EmailField(
        max_length=60,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        max_length=100, blank=True, verbose_name="Имя пользователя"
    )
    last_name = models.CharField(
        max_length=100, blank=True, verbose_name="Фамилия пользователя"
    )
    confirmation_code = models.CharField(max_length=6, default='000000')
    role = models.CharField(
        max_length=100, verbose_name="Роль", choices=ROLES, default=USER
    )
    bio = models.TextField(
        'Биография пользователя',
        blank=True
    )
    objects = UserManager()
    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def token(self) -> str:
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token().
        """
        return self._generate_jwt_token()

    def _generate_jwt_token(self) -> str:
        """
        Генерирует веб-токен JSON, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode(
            {"id": self.pk, "exp": int(dt.strftime("%s"))},
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        return token

class Category(models.Model):
    name = models.CharField(
        'имя категории',
        max_length=200
    )
    slug = models.SlugField(
        'слаг категории',
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Категории'

    def __str__(self):
        return f'{self.name} {self.name}'


class Genre(models.Model):
    name = models.CharField(
        'имя жанра',
        max_length=200
    )
    slug = models.SlugField(
        'cлаг жанра',
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Жанры'
        

    def __str__(self):
        return f'{self.name} {self.name}'


class Title(models.Model):
    name = models.CharField(
        'название',
        max_length=100,
        db_index=True
    )
    pub_date = models.IntegerField(
        'год',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=True
    )
    genre = models.ForeignKey(
        Genre,
        related_name='titles',
        verbose_name='жанр'
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.CharField(
        max_length=200
    )
    score = models.IntegerField('оценка')
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )
    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.CharField(
        'текст комментария',
        max_length=200
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор'
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )
