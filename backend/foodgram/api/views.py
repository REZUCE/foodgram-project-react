from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import views
from users.models import CustomUser


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser
    serializer_class = CustomUser