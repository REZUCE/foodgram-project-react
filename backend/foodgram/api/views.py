from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django.contrib.auth import get_user_model

User = get_user_model()

