from rest_framework import serializers
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer, UserCreateSerializer
from django.contrib.auth import get_user_model
from users.models import CustomUser, Subscription
from recipes.models import Tag, Recipe


class CustomUserSerializer(UserSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор модели пользователя."""

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """
        Дополнительное поле, которое
        никак не взаимодействует с базой данных.
        """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        # obj - это сериализуемый пользователь
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели тег."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепт."""

    class Meta:
        model = Recipe
        fields = '__all__'
