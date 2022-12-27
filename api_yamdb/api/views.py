import random

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrReadOnlyMy, AuthorAndModeratorOrReadOnly
from .serializers import CheckConfirmationCodeSerializer, SendCodeSerializer, UserSerializer, \
    UserMeSerializer, TitleReWriteSerializer, TitleReadSerializer, CategorySerializer, GenreSerializer, \
    ReviewSerializer, CommentSerializer

from reviews.models import User, Title, Category, Genre, Review


@api_view(["POST"])
@permission_classes([AllowAny])
def get_jwt(request):
    serializer = CheckConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if check_password(confirmation_code, user.confirmation_code):
        token = str(AccessToken.for_user(user))
        return Response({'access': token}, status=status.HTTP_201_CREATED)
    user.confirmation_code = "000000"
    user.save()
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def send_code(request):
    serializer = SendCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = request.data.get("email", False)
    username = request.data.get("username", False)
    confirmation_code = "".join(map(str, random.sample(
        range(settings.CONFIRMCODE_MAX_LENGTH), settings.CONFIRMCODE_LENGTH)))
    try:
        user, created = User.objects.get_or_create(email=email, username=username)
    except IntegrityError:
        return Response(
            'Такой логин или email уже существуют',
            status=status.HTTP_400_BAD_REQUEST
            )
    user.confirmation_code = make_password(
        confirmation_code, salt=None, hasher="default"
    )
    user.save()
    send_mail(
        "Code",
        confirmation_code,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    return Response(
        serializer.initial_data, status=status.HTTP_200_OK
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_patch_me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = UserMeSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserMeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')).order_by('name')
    serializer_class = TitleReWriteSerializer
    permission_classes = (IsAdminOrReadOnlyMy,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return TitleReadSerializer
        return TitleReWriteSerializer

class CategoryGenreMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAdminOrReadOnlyMy
    ]
    filter_backends = (SearchFilter,)
    search_fields = ('name', 'slug')
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreMixin):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixin):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AuthorAndModeratorOrReadOnly,)

    def get_title_id(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title_id().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title_id())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorAndModeratorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)
