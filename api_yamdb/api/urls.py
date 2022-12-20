from rest_framework.routers import DefaultRouter

from django.urls import path, include

from api.views import (
    TitleViewSet,
    CategoryViewSet,
    GenreViewSet,
)


router_v1 = DefaultRouter()
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]