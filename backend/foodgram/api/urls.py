from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TagViewSet, RecipeViewSet,
    CustomUserViewSet, IngredientViewSet,
    APIFavorite, APISubscription,
    APIShoppingCart, download_shopping
)

app_name = 'api'

# Routers - используются с viewsets
router = DefaultRouter()
# Создаем необходимый набор эндпоинтов
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(
        'recipes/<int:id>/shopping_cart/',
        APIShoppingCart.as_view(),
        name='shopping_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        download_shopping,
        name='download_shopping'
    ),
    path(
        'recipes/<int:id>/favorite/',
        APIFavorite.as_view(),
        name='favorite'
    ),
    path(
        'users/<int:id>/subscribe/',
        APISubscription.as_view(),
        name='subscription',
    ),
    path('auth/', include('djoser.urls.authtoken')),
    # Подключение эндпоинтов из router
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
