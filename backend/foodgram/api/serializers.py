from rest_framework import serializers
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer, UserCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
