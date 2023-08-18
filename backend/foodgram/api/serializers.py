from rest_framework import serializers
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer, UserCreateSerializer
from django.contrib.auth import get_user_model
from users.models import CustomUser, Subscription


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
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()
