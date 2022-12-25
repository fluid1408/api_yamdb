import random

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets

from django.conf import settings
from reviews.models import Title, Category, Genre, User, Review

from .filters import TitleFilter
from .serializers import (
    TitleReadSerializer,
    TitleReWriteSerializer,
    CategorySerializer,
    GenreSerializer,
    UserSerializer,
    SendCodeSerializer,
    CheckConfirmationCodeSerializer,
    CommentSerializer,
    ReviewSerializer,
    IsNotAdminUserSerializer,

)
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnlyMy,
    IsAdminModeratorOrReadOnlyVy
)
from rest_framework.permissions import AllowAny, IsAuthenticated


@api_view(["POST"])
@permission_classes([AllowAny])
def get_jwt(request):
    username = request.data.get("username")
    confirmation_code = request.data.get("confirmation_code")
    serializer = CheckConfirmationCodeSerializer(data=request.data)

    if serializer.is_valid():
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                serializer.errors,
                status=status.HTTP_404_NOT_FOUND)
        if check_password(confirmation_code, user.confirmation_code):
            token = AccessToken.for_user(user)
            user.confirmation_code = 0
            user.save()
            return Response({"access": str(token)})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def send_code(request):
    serializer = SendCodeSerializer(data=request.data)
    if serializer.is_valid():
        email = request.data.get("email", False)
        username = request.data.get("username", False)
        confirmation_code = "".join(map(str, random.sample(range(10), 6)))
        if not User.objects.filter(username=username, email=email).exists():
            user = User.objects.create(username=username, email=email)
        else:
            user = User.objects.get(username=username, email=email)
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
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me')
    def get_current_user_info(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = IsNotAdminUserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)

    def patch(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        return Response(
            'Вы не авторизованы',
            status=status.HTTP_401_UNAUTHORIZED)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    )
    serializer_class = TitleReWriteSerializer
    permission_classes = (IsAdminOrReadOnlyMy,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return TitleReadSerializer
        return TitleReWriteSerializer


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnlyMy, )
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnlyMy, )
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOrReadOnlyVy,)

    def get_title_id(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title_id().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title_id())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorOrReadOnlyVy,)

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
