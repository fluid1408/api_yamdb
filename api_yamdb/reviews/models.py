from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractUser
)
from django.core.validators import MaxValueValidator, MinValueValidator

from .validators import validate_username, validate_year
from django.conf import settings


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
        validators=(validate_username,),
        max_length=settings.USERNAME_MAX_LENGTH,
        unique=True,
    )
    email = models.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        'роль',
        max_length=20,
        choices=ROLES,
        default=USER,
        blank=True
    )
    bio = models.TextField(
        'биография',
        blank=True,
    )
    first_name = models.CharField(
        'имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        'фамилия',
        max_length=150,
        blank=True
    )
    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=255,
        null=True,
        blank=False,
        default='XXXX'
    )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.role == self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR or self.is_admin

    @property
    def is_user(self):
        return self.role == self.USER

    class Meta:
        ordering = ('username',)


class Group(models.Model):
    name = models.CharField(
        max_length=settings.GROUP_MAX_LENGTH
    )
    slug = models.SlugField(
        unique=True,
        db_index=True,
        max_length=settings.SLUG_MAX_LENGTH

    )

    def __str__(self):
        return f'{self.name}'


class Category(Group):
    class Meta:
        verbose_name = 'Категории'




class Genre(Group):
    class Meta:
        verbose_name = 'Жанры'



class Title(models.Model):
    name = models.CharField(
        'название',
        max_length=200,
        db_index=True
    )
    year = models.IntegerField(
        'год',
        validators=[validate_year],
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='категория',
        null=True,
        blank=True
    )
    description = models.TextField(
        'описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='жанр'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews',
        default=''
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(1, 'от 1 до 10'),
            MaxValueValidator(10, 'от 1 до 10')
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )
