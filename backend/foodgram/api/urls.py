from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, RecipeViewSet, CustomUserViewSet


app_name = 'api'

# Routers - используются с viewsets
router = DefaultRouter()
# Создаем необходимый набор эндпоинтов
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    # Подключение эндпоинтов из router
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
