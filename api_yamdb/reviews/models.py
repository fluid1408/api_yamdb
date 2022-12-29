from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .validators import validate_year, validate_username


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
        max_length=max(len(role) for role, _ in ROLES),
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
        max_length=settings.NAME_MAX_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        'фамилия',
        max_length=settings.NAME_MAX_LENGTH,
        blank=True
    )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        ordering = ('username',)


class GenreCategory(models.Model):
    name = models.CharField(
        max_length=settings.GROUP_MAX_LENGTH
    )
    slug = models.SlugField(
        unique=True,
        db_index=True,
        max_length=settings.SLUG_MAX_LENGTH

    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(GenreCategory):
    class Meta(GenreCategory.Meta):
        verbose_name = 'Категория произведения'


class Genre(GenreCategory):
    class Meta(GenreCategory.Meta):
        verbose_name = 'Жанры произведения'


class Title(models.Model):
    name = models.CharField(
        'название',
        max_length=settings.TITLE_MAX_LENGTH,
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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class ReviewComment(models.Model):
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        default=''
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return self.text

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Review(ReviewComment):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(1, 'от 1 до 10'),
            MaxValueValidator(10, 'от 1 до 10')
        ]
    )

    class Meta(ReviewComment.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='Уникальный обзор'
            ),
        ]


class Comment(ReviewComment):
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta(ReviewComment.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['review', 'author'],
                name='Уникальный комментарий'
            ),
        ]
