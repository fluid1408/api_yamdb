from rest_framework import permissions, status, viewsets
from django.core.mail import EmailMessage
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Category, Genre, Review, Title, User
from .serializers import UsersSerializer, SignUpSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )

class APISignup(APIView):
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_text'],
            to=[data['to_email']]
        )
        email.send()

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email_text = (
            f'Здравствуйте, {user.username}. '
            f'Код подтверждения для доступа к API: {user.confirmation_code}. '
            f'Не рассказывайте его никому'
        )
        data = {
            'email_text': email_text,
            'to_email': user.email,
            'email_subject': 'Код подтверждения для доступа к API'
        }
        self.send_email(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class APIGetToken(APIView):
    pass
