from rest_framework.routers import DefaultRouter

from django.urls import path, include

from .views import (
    send_confirmation_code,
    get_jwt,
    TitleViewSet,
    CategoryViewSet,
    GenreViewSet,
    UserViewSet,
)
from .views import APIUser


router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet)
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')


urlpatterns = [
    path('v1/auth/signup/', send_confirmation_code, name='get_token'),
    path('v1/auth/token/', get_jwt, name='send_confirmation_code'),
    path('v1/users/me/', APIUser.as_view()),
    path('v1/', include(router_v1.urls)),
]