from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
from rest_framework.decorators import action
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.contrib.auth import get_user_model
from users.models import Subscription
from recipes.models import Tag, Recipe, Ingredient, Favorite, ShoppingCart
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import TagSerializer, RecipesSerializer, RecipeCreateSerializer, \
    IngredientSerializer, FavoriteSerializer, ShowSubscriptionSerializer, SubscriptionSerializer, ShoppingCartSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    @action(
        methods=("get",),
        detail=False,
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPagination

    )
    def subscriptions(self, request):
        """
        Получить пользователей на которых подписан текущий пользователь.
        """

        subscription = User.objects.filter(author__user=request.user)
        # Подписки запихнули в пагинацию
        page = self.paginate_queryset(subscription)
        # Передаем request - это объект запроса, который содержит
        # информацию о текущем запросе, включая параметры пагинации,
        serializer = ShowSubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    # def dispatch(self, request, *args, **kwargs):
    #     res = super().dispatch(request, *args, **kwargs)
    #     from django.db import connection
    #     print(len(connection.queries))
    #     for q in connection.queries:
    #         print('>>>>', q['sql'])
    #     return res

    def get_queryset(self):
        """
        Для оптимизации запросов к бд.
        """

        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'recipe_tags__tag'
        ).all()
        return recipes

    def get_serializer_class(self):
        """
        Под каждый тип запросов свой serializer.
        """

        if self.action in ('create', 'update'):
            return RecipeCreateSerializer
        return RecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class APIFavorite(APIView):
    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        if not Favorite.objects.filter(
                user=request.user, recipe__id=id).exists():
            serializer = FavoriteSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(
                user=request.user,
                recipe=recipe).exists():
            Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)


class APISubscription(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'author': id
        }

        serializer = SubscriptionSerializer(
            data=data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        if Subscription.objects.filter(
                user=request.user,
                author=author).exists():
            subscription = get_object_or_404(
                Subscription, user=request.user, author=author
            )
            subscription.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)


class APIShoppingCart(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        if not ShoppingCart.objects.filter(
                user=request.user, recipe__id=id).exists():
            serializer = ShoppingCartSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        if ShoppingCart.objects.filter(
                user=request.user,
                recipe__id=id).exists():
            ShoppingCart.objects.filter(
                user=request.user,
                recipe__id=id
            ).delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)
