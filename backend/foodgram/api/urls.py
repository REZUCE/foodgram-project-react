from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, RecipeViewSet,
    CustomUserViewSet, IngredientViewSet,
    download_shopping
)

app_name = 'api'

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        download_shopping,
        name='download_shopping'
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
