import random
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status, permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import AccessToken

from django.conf import settings
from reviews.models import Title, Category, Genre, User
from .serializers import (
    TitleSerializer,
    CategorySerializer,
    GenreSerializer,
    UserSerializer,
    SendCodeSerializer,
    CheckConfirmationCodeSerializer,

)
from .permissions import (
    IsAuthorOrReadOnly,
    IsAdmin,
    IsAuthorOrAdminOrModerator,
    IsAdminUserOrReadOnly,
)
from rest_framework.permissions import AllowAny, IsAuthenticated

@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    serializer = SendCodeSerializer(data=request.data)
    email = request.data.get('email', False)
    username = request.data.get('username', False)
    if serializer.is_valid():
        confirmation_code = ''.join(map(str, random.sample(range(10), 6)))
        user = User.objects.filter(email=email).exists()
        if not user:
            User.objects.create_user(email=email, username=username)
        User.objects.filter(email=email).update(
            confirmation_code=make_password(confirmation_code, salt=None, hasher='default')
        )
        mail_subject = 'Код подтверждения для доступа к API! '
        message = (
            f'''
            Здравствуйте! {username}
            Код подтверждения для доступа к API: {confirmation_code}
            С уважением
            Yamdb
            '''
        )
        send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False, )
        text_message = (
            f'Код отправлен на адрес {email}. '
            'Проверьте раздел SPAM'
        )
        return Response(text_message, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt(request):
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')
    if not username or not confirmation_code:
        return Response(
            'Одно или несколько обязательных полей пропущены',
            status=status.HTTP_400_BAD_REQUEST
        )

    if not User.objects.filter(username=username).exists():
        return Response(
            'Имя пользователя неверное',
            status=status.HTTP_404_NOT_FOUND
        )

    user = User.objects.get(username=username)
    if check_password(confirmation_code, user.confirmation_code):
        token = AccessToken.for_user(user)
        return Response(
            {
                'access': str(token)
            }
        )

    return Response(
        'Код подтверждения неверен',
        status=status.HTTP_400_BAD_REQUEST
    )



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    permission_classes = [IsAdmin]
    search_fields = ['user__username', ]

class APIUser(APIView):
    @permission_classes([IsAuthenticated])
    def get(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response('Вы не авторизованы', status=status.HTTP_401_UNAUTHORIZED)


    def patch(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Вы не авторизованы', status=status.HTTP_401_UNAUTHORIZED)



class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAuthorOrReadOnly]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthorOrReadOnly]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthorOrReadOnly]
