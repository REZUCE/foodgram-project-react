from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django.contrib.auth import get_user_model
from users.models import Subscription
from .pagination import CustomPagination
from .serializers import SubscriptionSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=('get',),
        url_path='subscriptions',
        permissions_clases=(IsAuthenticated,)

    )
    def subscriptions(self, request):
        subscription = Subscription.objects.filter(user=request.user)
        # Позволяет пагинировать список авторов на основе данных из запроса.
        paginator = self.pagination_class()
        page = self.paginate_queryset(subscription)
        # Передаем request - это объект запроса, который содержит
        # информацию о текущем запросе, включая параметры пагинации,
        serializer = SubscriptionSerializer(
            page,
            many=True,
        )
        return paginator.get_paginated_response(serializer.data)
