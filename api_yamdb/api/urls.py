from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, TitleViewSet, CategoryViewSet, GenreViewSet, ReviewViewSet, CommentViewSet, \
    send_code, get_jwt

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet)
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
    r'/comments', CommentViewSet, basename='comments'
)


urlpatterns = [
    path('v1/auth/signup/', send_code, name='get_token'),
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', get_jwt, name='get_token'),
]
